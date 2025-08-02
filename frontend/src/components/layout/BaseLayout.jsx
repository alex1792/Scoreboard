import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import '../../styles/style.css';

const BaseLayout = () => {
  const { currentUser, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = (e) => {
    e.preventDefault();
    logout();
    navigate('/');
  };

  return (
    <>
      <nav>
        <h1><Link to="/">Score Board</Link></h1>
        <ul>
          <li><Link to="/">Score Board</Link></li>
          <li><Link to="/tournaments">Tournaments</Link></li>
          {isAuthenticated && currentUser && currentUser.username ? (
            <>
              <li><span>Welcome, {currentUser.username}</span></li>
              <li>
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
        <Outlet />
      </div>
    </>
  );
};

export default BaseLayout;