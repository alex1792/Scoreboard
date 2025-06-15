import { useState, useEffect } from 'react';
import io from 'socket.io-client';

const socket = io('/admin'); // 與後端 /admin namespace 建立連線

const ChangeUserStaus = () => {
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('user');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // request information for updating user role
      const requestInfo = {
        url: 'http://localhost:5001/api/admin/upate_user_role',
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ 
          username,
          role 
        }),
      };

      const response = await fetch(requestInfo.url, requestInfo);
      if (!response.ok) throw new Error('Update failed');

      const result = await response.json();
      // console.log('Update successful:', result);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="admin-form">
      <h1>Update User Role</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input
          name="username"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label htmlFor="role">Set Role</label>
        <select
          name="role"
          id="role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          required
        >
          <option value="admin">Admin</option>
          <option value="umpire">Umpire</option>
          <option value="user">User</option>
        </select>

        <input type="submit" value="Update Role" />
      </form>
    </div>
  );
};

export default ChangeUserStaus;