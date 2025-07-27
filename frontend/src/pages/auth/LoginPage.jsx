import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoginForm from './LoginForm';
import '../../styles/pages/auth/LoginPage.css';

function LoginPage() {
  const navigate = useNavigate();
  const { currentUser, isAuthenticated } = useAuth();

  // 如果已經登入，導向首頁
  if (isAuthenticated && currentUser) {
    return (
      <div className="login-page">
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
      </div>
    );
  }

  return (
    <div className="login-page">
      <LoginForm />
    </div>
  );
}

export default LoginPage;
