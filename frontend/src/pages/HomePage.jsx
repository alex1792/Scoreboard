import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useContext } from 'react';
import { useFetchUmpireMatchId } from '../api/api';

const Home = ({ currentUser }) => {
  const [myMatchId, setMyMatchId] = useState(null);
  const navigate = useNavigate();

  // get umpire's match and save it, so that the link
  // will be valid to be displayed
  useFetchUmpireMatchId(currentUser, setMyMatchId);

  return (
    <>
      <header className="header">
        <h1>Welcome to the Score Board</h1>
        <p>Your one-stop platform for managing matches and scores.</p>
      </header>

      <main className="content-container">
        <section className="card">
          <h2>General Features</h2>
          <div className="admin-icons">
            {currentUser?.role === 'umpire' && myMatchId && (
              <div className="admin-icon-item">
                <Link to={`/matches/${myMatchId}`}>
                  <img src="/documents-search-icon.png" alt="View Scoreboard" className="admin-icon" />
                  <span>View Scoreboard</span>
                </Link>
              </div>
            )}
            
            <div className="admin-icon-item">
                <Link to={`/tournaments`}>
                  <img src="/winning-cup-icon.png" alt="View All Tournaments" className="admin-icon" />
                  <span>View All Tournaments</span>
                </Link>
            </div>
            <div className="admin-icon-item">
              <Link to="/matches">
                <img src="/documents-search-icon.png" alt="Check All Matches" className="admin-icon" />
                <span>Check All Matches</span>
              </Link>
            </div>
            {currentUser?.role === 'admin' && (
              <>
                <div className="admin-icon-item">
                  <Link to="/admin/create-tournament">
                    <img src="/add-date-calendar-icon.png" alt="Create Tournament" className="admin-icon" />
                    <span>Create Tournament</span>
                  </Link>
                </div>
                <div className="admin-icon-item">
                  <Link to="/admin/set-umpire">
                    <img src="/file-setting-icon.png" alt="Match Management" className="admin-icon" />
                    <span>Match Management</span>
                  </Link>
                </div>
                <div className="admin-icon-item">
                  <Link to="/admin/users">
                    <img src="/manage-icon.png" alt="User Management" className="admin-icon" />
                    <span>User Management</span>
                  </Link>
                </div>
                <div className="admin-icon-item">
                  <Link to="/admin/upload-schedule">
                    <img src="/upload-arrow-icon.png" alt="Upload Schedule" className="admin-icon" />
                    <span>Upload Schedule</span>
                  </Link>
                </div>
              </>
            )}
          </div>
        </section>

        {/* {currentUser?.role === 'admin' && (
          <section className="card admin-section">
            <div className="admin-management">
              <h3>Match Management</h3>
              <ul className="link-list">
                <li><Link to="/admin/set-umpire">Manage Umpires</Link></li>
                <li><Link to="/admin/users">Check All Users</Link></li>
                <li><Link to="/admin/manage-matches">Manage Matches</Link></li>
                <li><Link to="/admin/create-match">Create New Match</Link></li>
                <li><Link to="/admin/update-user-role">Update User Role</Link></li>
                <li><Link to="/admin/upload-schedule">Uplaod Match Schedule</Link></li>
              </ul>
            </div>
          </section>
        )} */}
      </main>
    </>
  );
};

export default Home;
