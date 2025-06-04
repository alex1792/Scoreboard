import React from 'react';
import { Link } from 'react-router-dom';

const Home = ({ currentUser }) => {
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
              <li><Link to="/scoreboard">View Score Board</Link></li>
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
