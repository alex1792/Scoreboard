import { useState } from 'react';
import './LoginForm.css';

function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:5001/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        localStorage.setItem('access_token', data.data.access_token);
        if (onLogin) onLogin(data.data.user);
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Network error, please try again later');
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo">
            🏸
          </div>
          <h1>Welcome Back</h1>
          <p>Please login to your account</p>
        </div>
        
        {error && <div className="error-message">⚠️ {error}</div>}
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <span className="input-icon">👤</span>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="username" className="form-label">Username</label>
          </div>
          
          <div className="input-group">
            <span className="input-icon">🔒</span>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="password" className="form-label">Password</label>
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="loading-spinner">⏳</span>
            ) : (
              'Login'
            )}
          </button>
        </form>
        
        <div className="login-footer">
          <p>Don't have an account？ <a href="/register">Register</a></p>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;
