// RegisterForm.jsx
import React from 'react';

function RegisterForm() {
  const handleSubmit = (e) => {
    e.preventDefault();
    // 這裡可以加上註冊邏輯
  };

  return (
    <div>
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input name="username" id="username" required />
        <label htmlFor="password">Password</label>
        <input type="password" name="password" id="password" required />
        <input type="submit" value="Register" />
      </form>
    </div>
  );
}

export default RegisterForm;
