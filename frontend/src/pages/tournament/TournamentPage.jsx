import { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { fetchInfoFromBackend } from '../../api/api';
import '../../styles/pages/tournament/TournamentPage.css';

const TournamentPage = () => {
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { currentUser } = useContext(AuthContext);

  // Fetch tournaments from backend
  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        console.log('=== Starting to fetch tournaments ===');
        
        const data = await fetchInfoFromBackend('http://localhost:5001/api/tournaments');
        
        console.log('=== Response received ===');
        console.log('Full response:', data);
        
        if (data?.status === 'success') {
          console.log('Fetched tournaments:', data.data);
          setTournaments(data.data);
        } else {
          console.error('API returned error:', data?.message || 'Unknown error');
          setError(data?.message || 'Unknown error');
        }
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err.message || 'Network error');
      } finally {
        console.log('Fetch completed, setting loading to false');
        setLoading(false);
      }
    };

    fetchTournaments();
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return 'TBD';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      return 'Invalid Date';
    }
  };

  // 檢查用戶是否有管理權限
  const hasAdminAccess = () => {
    return currentUser && (currentUser.role === 'admin' || currentUser.role === 'host' || currentUser.role === 'organizer');
  };

  if (error) {
    return (
      <div className="container">
        <h1 className="page-title">All Tournaments</h1>
        <div className="error-message">
          Error: {error}
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container">
        <h1 className="page-title">All Tournaments</h1>
        <div className="loading">Loading tournaments...</div>
      </div>
    );
  }

  return (
    <>
      <div className="container">
        <h1 className="page-title">All Tournaments</h1>

        <div className="tournaments-grid">
          {tournaments.length > 0 ? (
            tournaments.map((tournament) => (
              <div key={tournament.id} className="tournament-card-wrapper">
                <div className="tournament-card">
                  <div className="tournament-header">
                    <div className="tournament-id">#{tournament.id}</div>
                  </div>
                  
                  <div className="tournament-name">
                    {tournament.name}
                  </div>

                  <div className="tournament-info">
                    <div className="info-item">
                      <span className="info-label">Start Date:</span>
                      <span className="info-value">{formatDate(tournament.start_date)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">End Date:</span>
                      <span className="info-value">{formatDate(tournament.end_date)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Status:</span>
                      <span className="info-value">{tournament.status || 'TBD'}</span>
                    </div>
                    
                    <div className="info-item">
                      <span className="info-label">Location:</span>
                      <span className="info-value">{tournament.location || 'TBD'}</span>
                    </div>
                    
                    {tournament.registration_deadline && (
                      <div className="info-item">
                        <span className="info-label">Registration Deadline:</span>
                        <span className="info-value">{formatDate(tournament.registration_deadline)}</span>
                      </div>
                    )}
                  </div>

                  <div className="tournament-actions">
                    <Link 
                      to={`/tournaments/${tournament.id}`}
                      className="view-details-btn"
                    >
                      View Details
                    </Link>
                    <Link 
                      to={`/tournaments/${tournament.id}/signup`}
                      className="signup-btn"
                    >
                      Sign Up
                    </Link>
                    
                    {/* 只有管理員才能看到查看報名信息的按鈕 */}
                    {hasAdminAccess() && (
                      <Link 
                        to={`/tournaments/${tournament.id}/check-registration`}
                        className="view-registrations-btn"
                      >
                        View Registrations
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="no-tournaments">No tournaments found</div>
          )}
        </div>
      </div>
    </>
  );
};

export default TournamentPage;
