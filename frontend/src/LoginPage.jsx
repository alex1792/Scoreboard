import React from 'react';
import LoginForm from './LoginForm';

function LoginPage() {
  const handleLogin = (user) => {
    console.log("登入成功，用戶資訊:", user);
    // 這裡可以更新全域狀態或跳轉頁面
  };

  return <LoginForm onLogin={handleLogin} />;
}

export default LoginPage;
