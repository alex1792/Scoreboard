import { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

const Users = () => {
  const [users, setUsers] = useState([]);

  // listen for user role updates from backend server
  const socketRef = useRef(null);
  useEffect(() => {
    socketRef.current = io('http://localhost:5001/user_role_update', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000
    });

    socketRef.current.on('connect', () => {
      // console.log('Socket connected!');
    });

    socketRef.current.on('user_role_updated', (data) => {
      // console.log('User role updated:', data);
      fetchUsers();
    });

    return () => {
      socketRef.current.disconnect();
    }
  }, []);

  // fetch all user data from backend server
  const fetchUsers = () => {
    const token = localStorage.getItem('access_token');
    fetch('http://localhost:5001/api/admin/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setUsers(data.data);
        } else {
          alert(data.message || '無法取得用戶資料');
        }
      })
      .catch(err => console.error("獲取用戶失敗:", err));
  };


  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <>
      <h1>All Users</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Umpire</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.username}</td>
              <td>{user.is_judge ? 'Yes' : 'No'}</td>
              <td>{user.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
};

export default Users;
