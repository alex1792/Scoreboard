import { useState, useEffect, useRef, useContext } from 'react';
import io from 'socket.io-client';
import { fetchUsers, updateUserRole } from '../../api/api';
import { AuthContext } from '../../context/AuthContext';
import '../../styles/pages/admin/UsersPage.css';

const UserCard = ({ user, onRoleUpdate, currentUserRole }) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [selectedRole, setSelectedRole] = useState(user.role);

  const roleColorMap = {
    admin: '#4CAF50',
    umpire: '#FFC107',
    user: '#9E9E9E'
  };

  const roleColor = roleColorMap[selectedRole?.toLowerCase()] || '#ccc';

  // only admin can edit the role
  const canEdit = currentUserRole === 'admin';
  
  // 調試信息
  console.log('UserCard Debug:', {
    currentUserRole,
    canEdit,
    userRole: user.role,
    username: user.username
  });

  const handleRoleChange = async (newRole) => {
    if (!canEdit || newRole === user.role) return;

    // if the role is changed to admin, need to confirm
    if (newRole === 'admin' && user.role !== 'admin') {
      const confirmed = window.confirm(`確定要將 ${user.username} 提升為管理員嗎？`);
      if (!confirmed) {
        setSelectedRole(user.role);
        return;
      }
    }

    setIsUpdating(true);
    try {
      await updateUserRole(user.id, newRole);
      setSelectedRole(newRole);
      onRoleUpdate(user.id, newRole);
    } catch (error) {
      console.error('更新角色失敗:', error);
      setSelectedRole(user.role); // restore the original value
      alert('更新角色失敗，請重試');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="user-card" data-user-id={user.id}>
      <div className="user-attributes">
        <div className="user-id">#{user.id}</div>
        <div className="user-username">{user.username}</div>
        <div className="user-role">
          {canEdit ? (
            <select
              className={`role-select ${isUpdating ? 'updating' : ''}`}
              value={selectedRole}
              onChange={(e) => handleRoleChange(e.target.value)}
              disabled={isUpdating}
              style={{ 
                backgroundColor: roleColor + '20', 
                color: roleColor,
                border: `2px solid ${roleColor}`
              }}
            >
              <option value="user">USER</option>
              <option value="umpire">UMPIRE</option>
              <option value="admin">ADMIN</option>
            </select>
          ) : (
            <span 
              className="role-badge"
              style={{ backgroundColor: roleColor + '20', color: roleColor }}
            >
              {selectedRole?.toUpperCase()}
            </span>
          )}
          {isUpdating && <span className="updating-indicator">⏳</span>}
        </div>
      </div>
    </div>
  );
};

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useContext(AuthContext);

  // 調試信息
  console.log('Users Component Debug:', {
    currentUser,
    currentUserRole: currentUser?.role,
    isAdmin: currentUser?.role === 'admin'
  });

  // fetch users data
  const loadUsers = async () => {
    try {
      setLoading(true);
      const userData = await fetchUsers();
      setUsers(userData);
    } catch (err) {
      console.error("獲取用戶失敗:", err);
    } finally {
      setLoading(false);
    }
  };

  // update local users data
  const handleRoleUpdate = (userId, newRole) => {
    setUsers(prevUsers => 
      prevUsers.map(user => 
        user.id === userId ? { ...user, role: newRole } : user
      )
    );
  };

  // Socket connection
  const socketRef = useRef(null);
  useEffect(() => {
    socketRef.current = io('http://localhost:5001/user_role_update', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000
    });

    socketRef.current.on('connect', () => {
      console.log('Socket connected!');
    });

    socketRef.current.on('user_role_updated', (data) => {
      console.log('User role updated:', data);
      loadUsers(); // reload users data
    });

    return () => {
      socketRef.current.disconnect();
    }
  }, []);

  // initial load
  useEffect(() => {
    loadUsers();
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">All Users</h1>
        </div>
        <div className="loading-container">
          <div className="loading-spinner">⏳</div>
          <p>Loading users data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">All Users</h1>
        <div className="user-stats">
          <span className="stat-item">Total: {users.length}</span>
          <span className="stat-item">Admin: {users.filter(u => u.role === 'admin').length}</span>
          <span className="stat-item">Umpire: {users.filter(u => u.role === 'umpire').length}</span>
          <span className="stat-item">User: {users.filter(u => u.role === 'user').length}</span>
        </div>
      </div>
      
      <div className="users-grid">
        {users.map((user) => (
          <UserCard 
            key={user.id} 
            user={user} 
            onRoleUpdate={handleRoleUpdate}
            currentUserRole={currentUser?.role}
          />
        ))}
      </div>
    </div>
  );
};

export default Users;
