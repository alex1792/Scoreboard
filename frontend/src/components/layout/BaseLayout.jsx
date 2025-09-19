import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import '../../styles/style.css';

const BaseLayout = () => {
  const { currentUser, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation(); // 獲取當前路由

  const handleLogout = (e) => {
    e.preventDefault();
    logout();
    navigate('/');
  };

  // Back 按鈕處理函數
  const handleBack = () => {
    // 檢查是否有歷史記錄可以返回
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      // 如果沒有歷史記錄，回到首頁
      navigate('/');
    }
  };

  // 決定是否顯示 Back 按鈕
  const shouldShowBackButton = () => {
    // 首頁不顯示 Back 按鈕
    if (location.pathname === '/') return false;
    
    // 登入/註冊頁面不顯示 Back 按鈕
    if (location.pathname === '/login' || location.pathname === '/register') return false;
    
    // 其他頁面都顯示 Back 按鈕
    return true;
  };

  return (
    <>
      <nav>
        <h1><Link to="/">Score Board</Link></h1>
        <ul>
          <li><Link to="/">Score Board</Link></li>
          <li><Link to="/tournaments">Tournaments</Link></li>
          <li><Link to="/about">About</Link></li>
          {isAuthenticated && currentUser && currentUser.username ? (
            <>
              <li><span>Welcome, {currentUser.username}</span></li>
              <li>
                {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                <a href="#" onClick={handleLogout} className="nav-link">
                  Logout
                </a>
              </li> 
            </>
          ) : (
            <>
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/register">Register</Link></li>
            </>
          )}
        </ul>
      </nav>
      <div className="content">
        {/* 添加 Back 按鈕 */}
        {shouldShowBackButton() && (
          <div className="back-button-container">
            <button className="back-btn" onClick={handleBack}>
              ← Back
            </button>
          </div>
        )}
        <Outlet />
      </div>
    </>
  );
};

export default BaseLayout;