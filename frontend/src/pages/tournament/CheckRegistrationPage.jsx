import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../../styles/pages/tournament/CheckRegistrationPage.css';

function CheckRegistrationPage() {
  const { tournamentId } = useParams();
  const [registrations, setRegistrations] = useState([]);
  const [tournament, setTournament] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRegistrations();
    fetchTournamentDetails();
  }, [tournamentId]);

  const fetchRegistrations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/home/tournament/${tournamentId}/registrations`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setRegistrations(data.data);
      } else {
        setError(data.message || 'Failed to fetch registrations');
      }
    } catch (err) {
      setError('Network error, please try again later');
      console.error("Fetch registrations error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTournamentDetails = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/home/tournaments/${tournamentId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setTournament(data.data);
      }
    } catch (err) {
      console.error("Fetch tournament details error:", err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return '#ffa500';
      case 'confirmed':
        return '#4caf50';
      case 'rejected':
        return '#f44336';
      default:
        return '#666';
    }
  };

  const getEventType = (eventName) => {
    if (eventName.includes('MS')) return 'Men Singles';
    if (eventName.includes('WS')) return 'Women Singles';
    if (eventName.includes('MD')) return 'Men Doubles';
    if (eventName.includes('WD')) return 'Women Doubles';
    if (eventName.includes('XD')) return 'Mixed Doubles';
    return eventName;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">⏳</div>
        <p>Loading registrations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">⚠️ {error}</div>
        <button onClick={fetchRegistrations} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="check-registration-container">
      <div className="header">
        <h1>Tournament Registrations</h1>
        {tournament && (
          <div className="check-registration-tournament-info">
            <h2>{tournament.name}</h2>
            <p>Location: {tournament.location}</p>
            <p>Date: {new Date(tournament.start_date).toLocaleDateString()} - {new Date(tournament.end_date).toLocaleDateString()}</p>
          </div>
        )}
      </div>

      <div className="stats-container">
        <div className="stat-card">
          <h3>Total Registrations</h3>
          <p className="stat-number">{registrations.length}</p>
        </div>
        <div className="stat-card">
          <h3>Confirmed</h3>
          <p className="stat-number">{registrations.filter(r => r.status === 'confirmed').length}</p>
        </div>
        <div className="stat-card">
          <h3>Pending</h3>
          <p className="stat-number">{registrations.filter(r => r.status === 'pending').length}</p>
        </div>
      </div>

      <div className="registrations-container">
        <h3>Registration Details</h3>
        
        {registrations.length === 0 ? (
          <div className="no-registrations">
            <p>No registrations found for this tournament.</p>
          </div>
        ) : (
          <div className="registrations-grid">
            {registrations.map((registration) => (
              <div key={registration.id} className="registration-card">
                <div className="registration-header">
                  <h4>{getEventType(registration.event_name)}</h4>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(registration.status) }}
                  >
                    {registration.status}
                  </span>
                </div>
                
                <div className="registration-details">
                  <div className="player-info">
                    <strong>Player:</strong> {registration.user_name}
                  </div>
                  
                  {registration.partner_name && (
                    <div className="partner-info">
                      <strong>Partner:</strong> {registration.partner_name}
                    </div>
                  )}
                  
                  <div className="group-info">
                    <strong>Group:</strong> {registration.group_name}
                  </div>
                  
                  <div className="date-info">
                    <strong>Registered:</strong> {new Date(registration.registration_date).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default CheckRegistrationPage;