import { createContext, useContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // 檢查是否有儲存的 token
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // 驗證 token 是否有效
      validateToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const validateToken = async (token) => {
    try {
      // 呼叫後端 API 驗證 token
      const response = await fetch('http://localhost:5001/api/auth/validate', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setCurrentUser(userData);
        setIsAuthenticated(true);
      } else {
        // token 無效，清除
        localStorage.removeItem('access_token');
        setIsAuthenticated(false);
        setCurrentUser(null);
      }
    } catch (error) {
      console.error('Token validation error:', error);
      localStorage.removeItem('access_token');
      setIsAuthenticated(false);
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = (userData, token) => {
    setCurrentUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('access_token', token);
  };

  const logout = () => {
    setCurrentUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ 
      currentUser, 
      setCurrentUser,
      isAuthenticated, 
      login, 
      logout, 
      loading 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
