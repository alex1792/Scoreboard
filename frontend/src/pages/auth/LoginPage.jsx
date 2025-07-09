import { useNavigate } from 'react-router-dom';
import LoginForm from './LoginForm';
import '../../styles/pages/auth/LoginPage.css';

function LoginPage({ setCurrentUser, currentUser}) {
  const navigate = useNavigate();

  const handleLogin = (user) => {
    setCurrentUser(user);
    navigate('/');
  };

  return (
    <div className="login-page">
      {currentUser ? (
        <div className="welcome-back">
          <div className="welcome-card">
            <div className="welcome-icon">🎉</div>
            <h2>Welcome Back, {currentUser.username}！</h2>
            <p>You're logging in as {currentUser.role}</p>
            <button 
              onClick={() => navigate('/')}
              className="go-home-button"
            >
              Home
            </button>
          </div>
        </div>
      ) : (
        <LoginForm onLogin={handleLogin} />
      )}
    </div>
  );
}

export default LoginPage;
