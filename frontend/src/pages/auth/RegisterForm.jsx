import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/pages/auth/RegisterForm.css';

function RegisterForm() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    email: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // 驗證必填欄位
    if (!formData.username || !formData.password || !formData.first_name || !formData.last_name) {
      setError('Please fill in all required fields');
      return;
    }
    
    // 驗證密碼
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:5001/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email || null
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('Registration successful! Please login with your new account.');
        navigate('/login');
      } else {
        setError(data.message || 'Registration failed');
      }
    } catch (err) {
      setError('Network error, please try again later');
      console.error("Registration error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <div className="logo">
            🏸
          </div>
          <h1>Create Account</h1>
          <p>Join our tournament management system</p>
        </div>
        
        {error && <div className="error-message">⚠️ {error}</div>}
        
        <form onSubmit={handleSubmit} className="register-form">
          <div className="input-group">
            <span className="input-icon"></span>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="username" className="form-label">Username *</label>
          </div>
          
          <div className="input-group">
            <span className="input-icon"></span>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="first_name" className="form-label">First Name *</label>
          </div>
          
          <div className="input-group">
            <span className="input-icon"></span>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="last_name" className="form-label">Last Name *</label>
          </div>
          
          <div className="input-group">
            <span className="input-icon"></span>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="email" className="form-label">Email (Optional)</label>
          </div>
          
          <div className="input-group">
            <span className="input-icon"></span>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="password" className="form-label">Password *</label>
          </div>
          
          <div className="input-group">
            <span className="input-icon"></span>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder=" "
            />
            <label htmlFor="confirmPassword" className="form-label">Confirm Password *</label>
          </div>
          
          <button 
            type="submit" 
            className="register-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="loading-spinner">⏳</span>
            ) : (
              'Create Account'
            )}
          </button>
        </form>
        
        <div className="register-footer">
          <p>Already have an account? <a href="/login">Login</a></p>
        </div>
      </div>
    </div>
  );
}

export default RegisterForm;
