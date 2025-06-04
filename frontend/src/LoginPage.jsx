import { useContext } from 'react';
import { AuthContext } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import LoginForm from './LoginForm';



function LoginPage() {
  const { currentUser, setCurrentUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = (user) => {
    setCurrentUser(user); // 更新 currentUser
    console.log("登入成功，用戶資訊:", user);
    // 這裡可以跳轉頁面或做其他處理
    navigate('/');
  };

  return (
    <div>
      {currentUser ? (
        <div>歡迎回來，{currentUser.username}！</div>
      ) : (
        <LoginForm onLogin={handleLogin} />
      )}
    </div>
  );
}

export default LoginPage;
