import React, { useState, useEffect } from 'react';
import BaseLayout from './BaseLayout';

const Users = () => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
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
