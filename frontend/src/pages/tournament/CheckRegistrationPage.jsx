import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../../styles/pages/tournament/CheckRegistrationPage.css';

function CheckRegistrationPage() {
  const { tournamentId } = useParams();
  const [registrations, setRegistrations] = useState([]);
  const [filteredRegistrations, setFilteredRegistrations] = useState([]);
  const [tournament, setTournament] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // 篩選狀態
  const [selectedEvent, setSelectedEvent] = useState('all');
  const [selectedGroup, setSelectedGroup] = useState('all');
  const [availableEvents, setAvailableEvents] = useState([]);
  const [availableGroups, setAvailableGroups] = useState([]);
  const [eventGroups, setEventGroups] = useState({}); // 存儲每個 event 對應的 groups

  // fetch all registrations and tournament details
  useEffect(() => {
    fetchRegistrations();
    fetchTournamentDetails();
  }, [tournamentId]);

  // set events and groups options
  useEffect(() => {
    if (tournament && tournament.events) {
      // set events options
      const events = tournament.events.map(event => event.name);
      setAvailableEvents(events);
      
      // set event-groups mapping, groups are under each event
      const groupsMap = {};
      tournament.events.forEach(event => {
        groupsMap[event.name] = event.groups.map(group => group.name);
      });
      setEventGroups(groupsMap);
    }
  }, [tournament]);

  // when select event, update the groups options
  useEffect(() => {
    if (selectedEvent !== 'all' && eventGroups[selectedEvent]) {
      setAvailableGroups(eventGroups[selectedEvent]);
    } else {
      setAvailableGroups([]);
    }
    setSelectedGroup('all'); // reset group options
  }, [selectedEvent, eventGroups]);

  // when select event or group, filter the registration
  useEffect(() => {
    filterRegistrations();
  }, [registrations, selectedEvent, selectedGroup]);

  const fetchRegistrations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/registrations/tournament/${tournamentId}/registrations`, {
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
      const response = await fetch(`http://localhost:5001/api/tournaments/${tournamentId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setTournament(data.data);
      }
    } catch (err) {
      console.error("Fetch tournament details error:", err);
    }
  };

  const filterRegistrations = () => {
    let filtered = [...registrations];

    // filter by event
    if (selectedEvent !== 'all') {
      filtered = filtered.filter(r => r.event_name === selectedEvent);
    }

    // select by group
    if (selectedGroup !== 'all') {
      filtered = filtered.filter(r => r.group_name === selectedGroup);
    }

    setFilteredRegistrations(filtered);
  };

  const resetFilters = () => {
    setSelectedEvent('all');
    setSelectedGroup('all');
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
          <h3>Filtered Results</h3>
          <p className="stat-number">{filteredRegistrations.length}</p>
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
        <div className="registrations-header">
          <h3 className="registrations-title">Registration Details</h3>
          
          {/* select event and group filter */}
          <div className="filters-container">
            <div className="filter-group">
              <label htmlFor="event-filter">Event:</label>
              <select 
                id="event-filter"
                value={selectedEvent}
                onChange={(e) => setSelectedEvent(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Events</option>
                {availableEvents.map(event => (
                  <option key={event} value={event}>
                    {getEventType(event)}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="group-filter">Group:</label>
              <select 
                id="group-filter"
                value={selectedGroup}
                onChange={(e) => setSelectedGroup(e.target.value)}
                className="filter-select"
                disabled={selectedEvent === 'all'}
              >
                <option value="all">
                  {selectedEvent === 'all' ? 'Select Event First' : 'All Groups'}
                </option>
                {availableGroups.map(group => (
                  <option key={group} value={group}>
                    {group}
                  </option>
                ))}
              </select>
            </div>

            <button onClick={resetFilters} className="reset-filters-btn">
              Reset
            </button>
          </div>
        </div>
        
        {filteredRegistrations.length === 0 ? (
          <div className="no-registrations">
            <p>
              {registrations.length === 0 
                ? "No registrations found for this tournament."
                : "No registrations match the selected filters."
              }
            </p>
            {registrations.length > 0 && (
              <button onClick={resetFilters} className="reset-filters-btn">
                Reset Filters
              </button>
            )}
          </div>
        ) : (
          <div className="registrations-grid">
            {filteredRegistrations.map((registration) => (
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