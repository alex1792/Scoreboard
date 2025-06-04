import React from 'react';
import BaseLayout from './BaseLayout';

const Users = ({ users }) => {
  return (
    <BaseLayout title="All Users">
      <h1>All Users</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Umpire</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.username}</td>
              <td>{user.is_judge ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </BaseLayout>
  );
};

export default Users;