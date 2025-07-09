import { Link, Outlet } from 'react-router-dom';
import '../../styles/style.css';

const BaseLayout = ({ currentUser }) => {
  return (
    <>
      <nav>
        <h1><Link to="/">Score Board</Link></h1>
        <ul>
          <li><Link to="/">Score Board</Link></li>
          <li><Link to="/matches">Matches</Link></li>
          {currentUser && currentUser.username ? (
            <>
              <li><span>Welcome, {currentUser.username}</span></li>
              <li><Link to="/logout">Logout</Link></li>
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