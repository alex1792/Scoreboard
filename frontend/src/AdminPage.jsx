import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import BaseLayout from './BaseLayout';

const socket = io('/admin'); // 與後端 /admin namespace 建立連線

const Admin = () => {
  const [username, setUsername] = useState('');
  const [isJudge, setIsJudge] = useState('true');

  useEffect(() => {
    socket.on('user_role_updated', (data) => {
      console.log('User role updated:', data);
      // 你可以根據實際需求更新畫面狀態
    });

    return () => {
      socket.off('user_role_updated');
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 提交資料到後端（視你的 API 實作方式而定）
    try {
      const response = await fetch('/api/admin/update-role', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, is_judge: isJudge === 'true' }),
      });

      if (!response.ok) throw new Error('Update failed');
      const result = await response.json();
      console.log('Update success:', result);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <BaseLayout>
        <div className="admin-form">
        <h1>Update User Role</h1>
        <form onSubmit={handleSubmit}>
            {/* Username input */}
            <label htmlFor="username">Username</label>
            <input
            name="username"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            />

            {/* Dropdown menu for is_judge */}
            <label htmlFor="is_judge">Set Judge Role</label>
            <select
            name="is_judge"
            id="is_judge"
            value={isJudge}
            onChange={(e) => setIsJudge(e.target.value)}
            required
            >
            <option value="true">True</option>
            <option value="false">False</option>
            </select>

            {/* Submit button */}
            <input type="submit" value="Update Role" />
        </form>
        </div>
    </BaseLayout>
  );
};

export default Admin;