import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import '../../styles/pages/tournament/CheckRegistrationPage.css';
import { fetchInfoToBackend, updateRegistrationStatus } from '../../api/api';
import { getRegistrationsByTournamentUrl, getTournamentUrl, getTournamentGenerateMatchesUrl } from '../../config/urls';

function CheckRegistrationPage() {
  const { tournamentId } = useParams();
  const [registrations, setRegistrations] = useState([]);
  const [filteredRegistrations, setFilteredRegistrations] = useState([]);
  const [tournament, setTournament] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState([]);
  
  // 篩選狀態
  const [selectedEvent, setSelectedEvent] = useState('all');
  const [selectedGroup, setSelectedGroup] = useState('all');
  const [availableEvents, setAvailableEvents] = useState([]);
  const [availableGroups, setAvailableGroups] = useState([]);
  const [eventGroups, setEventGroups] = useState({}); // 存儲每個 event 對應的 groups
  const [generating, setGenerating] = useState(false);

  const navigate = useNavigate();

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
      const response = await fetch(`${getRegistrationsByTournamentUrl(tournamentId)}`, {
        method: 'GET',
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
      const response = await fetch(`${getTournamentUrl(tournamentId)}`);
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

  const handleGenerateMatches = async () => {
    if (!window.confirm('Are you sure you want to generate matches for this tournament? This action cannot be undone.')) {
      return;
    }

    setGenerating(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getTournamentGenerateMatchesUrl(tournamentId)}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      console.log(data);
      
      if (data.status === 'success') {
        alert(`Successfully generated ${data.data?.length || 0} matches!`);
        // 可以選擇重新載入頁面或導航到比賽頁面
        // window.location.reload();
        navigate(`/tournaments/${tournamentId}/matches`);
      } else {
        alert(`Error: ${data.message || 'Failed to generate matches'}`);
      }
    } catch (error) {
      console.error('Generate matches error:', error);
      alert('Network error, please try again');
    } finally {
      setGenerating(false);
    }
  };

  const formatRegistrationDate = (dateString) => {
    if(!dateString) return 'Invalid date';

    try {
      const date = new Date(dateString);
      if(isNaN(date.getTime())) {
        return 'Invalid date';
      }

      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      console.error('Error formatting registration date:', error);
      return 'Invalid date';
    }
  };

  const handleStatusChange = async (registrationId, newStatus) => {
    setUpdatingStatus(prev => ({...prev, [registrationId]: true}));

    try {
      const response  = await updateRegistrationStatus(registrationId, newStatus);
      if(response.status === 'success') {
        setRegistrations(prev =>
          prev.map(reg => reg.id === registrationId ? {...reg, status: newStatus} : reg)
        );

        // update filtered registrations
        filterRegistrations();
      } else {
        alert(`Failed to update status: ${response.message}`);
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status, please try again');
    } finally {
      setUpdatingStatus(prev => ({...prev, [registrationId]: false}));
    }
  };

  // 修改狀態顯示組件
  const StatusDropdown = ({ registration }) => {
    const isUpdating = updatingStatus[registration.id];
    // const canEdit = hasEditPermission();
  
    // if (!canEdit) {
    //   return (
    //     <span 
    //       className="status-badge"
    //       style={{ backgroundColor: getStatusColor(registration.status) }}
    //     >
    //       {registration.status}
    //     </span>
    //   );
    // }
  
    return (
      <select
        value={registration.status}
        onChange={(e) => handleStatusChange(registration.id, e.target.value)}
        disabled={isUpdating}
        className="status-dropdown"
        style={{ 
          backgroundColor: getStatusColor(registration.status),
          color: 'white',
          border: 'none',
          borderRadius: '20px',
          padding: '4px 12px',
          fontSize: '0.8em',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          cursor: isUpdating ? 'not-allowed' : 'pointer'
        }}
      >
        <option value="pending">Pending</option>
        <option value="confirmed">Confirmed</option>
        <option value="cancelled">Cancelled</option>
      </select>
    );
  };


  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">⏳</div>
        <p>Loading registrations...</p>
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
        
        {/* 新增產生賽程按鈕 */}
        <div className="generate-matches-section">
          <button 
            onClick={handleGenerateMatches}
            disabled={generating || registrations.length === 0}
            className="generate-matches-btn"
          >
            {generating ? 'Generating...' : 'Generate Matches'}
          </button>
          {registrations.length === 0 && (
            <p className="generate-matches-hint">No registrations found. Please wait for players to sign up.</p>
          )}
        </div>

        <div className="upload-registration-section">
        <Link
          to={`/tournaments/${tournamentId}/upload-registration`}
          className="upload-registration-btn"
        >
          <img src="/upload-arrow-icon.png" alt="Upload" className="upload-icon" />
          Upload Registration File
        </Link>
          <p className="upload-registration-hint">Upload Excel file to bulk import registrations</p>
        </div>
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
                  <StatusDropdown registration={registration} />
                  {/* <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(registration.status) }}
                  >
                    {registration.status}
                  </span> */}
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
                    <strong>Registered:</strong> {formatRegistrationDate(registration.registration_date)}
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