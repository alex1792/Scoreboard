import { useNavigate } from 'react-router-dom';
import LoginForm from './LoginForm';



function LoginPage({ setCurrentUser, currentUser}) {
  const navigate = useNavigate();

  const handleLogin = (user) => {
    setCurrentUser(user); // 更新 currentUser
    // console.log("login successfully, user info:", user);
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
