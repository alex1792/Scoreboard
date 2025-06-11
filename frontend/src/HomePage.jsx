// import React from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useContext } from 'react';
// import { AuthContext } from './AuthContext';

const Home = ({ currentUser }) => {
  // const { currentUser } = useContext(AuthContext);
  // console.log("currentUser in Home:", currentUser);
  const [myMatchId, setMyMatchId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser?.role === 'umpire') {
      fetch(`http://localhost:5001/api/matches/umpire/${currentUser.id}`)
        .then(res => res.json())
        .then(result => {
          if (result.status === 'success' && result.data?.id) {
            setMyMatchId(result.data.id);
          }
        })
    }
  }, [currentUser]);

  return (
    <>
      <header className="header">
        <h1>Welcome to the Score Board</h1>
        <p>Your one-stop platform for managing matches and scores.</p>
      </header>

      <main className="content-container">
        <section className="card">
          <h2>General Features</h2>
          <ul className="link-list">
            {(currentUser?.id === 1 || currentUser?.role === 'umpire') && (
              <li>
                {/* <button onClick={handleViewScoreboard}>View Score Board</button> */}
                <Link to={`/matches/${myMatchId}`}>View Scoreboard</Link>
              </li>
            )}
            <li><Link to="/matches">Check All Matches</Link></li>
          </ul>
        </section>

        {currentUser?.role === 'admin' && (
          <section className="card admin-section">
            <h2>Admin Features</h2>
            <ul className="link-list">
              <li><Link to="/admin/set-umpire">Manage Umpires</Link></li>
              <li><Link to="/admin/users">Check All Users</Link></li>
              <li><Link to="/admin/manage-matches">Manage Matches</Link></li>
              <li><Link to="/admin/create-match">Create New Match</Link></li>
              <li><Link to="/admin/assign-umpire">Assign Umpire</Link></li>
            </ul>
          </section>
        )}
      </main>
    </>
  );
};

export default Home;
