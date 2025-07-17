import { useRef, useState, useContext, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMatchInfoListener } from '../../api/socketService';
import { useFetchMatchInfo, useFetchMatchInfoByTournament } from '../../api/api';
import { AuthContext } from '../../context/AuthContext';
import '../../styles/pages/match/matches.css';

const MatchesPage = ({ currentUser }) => {
  const { currentUser: contextUser } = useContext(AuthContext);
  const [matches, setMatches] = useState([]);
  const [filteredMatches, setFilteredMatches] = useState([]);
  const [animatingMatchId, setAnimatingMatchId] = useState(null);
  const socketRef = useRef(null);
  const { tournamentId } = useParams();

  // 篩選狀態
  const [selectedEvent, setSelectedEvent] = useState('all');
  const [selectedGroup, setSelectedGroup] = useState('all');
  const [availableEvents, setAvailableEvents] = useState([]);
  const [availableGroups, setAvailableGroups] = useState([]);
  const [eventGroups, setEventGroups] = useState({}); // 存儲每個 event 對應的 groups

  // 使用 props 中的 currentUser 或 context 中的 currentUser
  const user = currentUser || contextUser;

  // fetch match info from backend
  useFetchMatchInfoByTournament(setMatches, tournamentId);

  // match info listener
  useMatchInfoListener(socketRef, { setMatches, setAnimatingMatchId });

  // 設置 events 和 groups 選項
  useEffect(() => {
    if (matches.length > 0) {
      // 提取所有唯一的 events
      const events = [...new Set(matches.map(match => match.category))];
      setAvailableEvents(events);
      
      // 設置 event-groups 映射
      const groupsMap = {};
      events.forEach(event => {
        const eventMatches = matches.filter(match => match.category === event);
        const groups = [...new Set(eventMatches.map(match => match.group))];
        groupsMap[event] = groups;
      });
      setEventGroups(groupsMap);
    }
  }, [matches]);

  // 當選擇 event 時，更新 groups 選項
  useEffect(() => {
    if (selectedEvent !== 'all' && eventGroups[selectedEvent]) {
      setAvailableGroups(eventGroups[selectedEvent]);
    } else {
      setAvailableGroups([]);
    }
    setSelectedGroup('all'); // 重置 group 選項
  }, [selectedEvent, eventGroups]);

  // 當選擇 event 或 group 時，篩選比賽
  useEffect(() => {
    filterMatches();
  }, [matches, selectedEvent, selectedGroup]);

  const filterMatches = () => {
    let filtered = [...matches];

    // 按 event 篩選
    if (selectedEvent !== 'all') {
      filtered = filtered.filter(match => match.category === selectedEvent);
    }

    // 按 group 篩選
    if (selectedGroup !== 'all') {
      filtered = filtered.filter(match => match.group === selectedGroup);
    }

    setFilteredMatches(filtered);
  };

  const resetFilters = () => {
    setSelectedEvent('all');
    setSelectedGroup('all');
  };

  const getStatusColor = (status) => {
    const colorMap = {
      ended: '#4CAF50',
      ongoing: '#FFC107',
      pending: '#9E9E9E'
    };
    return {
      backgroundColor: `${colorMap[status.toLowerCase()]}20`,
      color: colorMap[status.toLowerCase()]
    };
  };

  const getEventType = (eventName) => {
    if (eventName.includes('MS')) return 'Men Singles';
    if (eventName.includes('WS')) return 'Women Singles';
    if (eventName.includes('MD')) return 'Men Doubles';
    if (eventName.includes('WD')) return 'Women Doubles';
    if (eventName.includes('XD')) return 'Mixed Doubles';
    return eventName;
  };

  // 檢查用戶權限
  const hasAdminAccess = () => {
    return user && (user?.role === 'admin' || user?.role === 'host' || user?.role === 'organizer');
  };

  return (
    <>
      <div className="container">
        <h1 className="page-title">Tournament Matches</h1>
        
        {hasAdminAccess() && (
          <div className="generate-match-schedule-btn-container">
            <Link to={`/admin/tournaments/${tournamentId}/generate-schedule`}>
              <button className="generate-match-schedule-btn">
                Generate Schedule
              </button>
            </Link>
          </div>
        )}

        {/* 統計信息 */}
        <div className="stats-container">
          <div className="stat-card">
            <h3>Total Matches</h3>
            <p className="stat-number">{matches.length}</p>
          </div>
          <div className="stat-card">
            <h3>Filtered Results</h3>
            <p className="stat-number">{filteredMatches.length}</p>
          </div>
          <div className="stat-card">
            <h3>Ongoing</h3>
            <p className="stat-number">{matches.filter(m => m.status === 'ongoing').length}</p>
          </div>
          <div className="stat-card">
            <h3>Completed</h3>
            <p className="stat-number">{matches.filter(m => m.status === 'ended').length}</p>
          </div>
        </div>

        {/* 篩選器 */}
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

        <div className="matches-grid">
          {filteredMatches.length > 0 ? (
            filteredMatches.map((match) => (
              <Link
                key={match.id}
                to={`/matches/${match.id}`}
                className="match-card-link"
              >
                <div
                  className={`match-card status-${match.status.toLowerCase()}${animatingMatchId === match.id ? ' animating' : ''}`}
                  data-match-id={match.id}
                >
                  <div className="match-header">
                    <div className="match-id">#{match.id}</div>
                    <div className="match-category">{match.category} - {match.group}</div>
                  </div>
                  
                  <div className="players">
                    <div className="player">
                      <div className="player-name">{match.player1}</div>
                    </div>

                    <div className="vs">vs</div>

                    <div className="player">
                      <div className="player-name">{match.player2}</div>
                    </div>
                  </div>

                  <div className="score">
                    {match.score1} : {match.score2}
                  </div>

                  <div className="status">
                    <span
                      className={`status-badge status-${match.status.toLowerCase()}`}
                      style={getStatusColor(match.status)}
                    >
                      {match.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="umpire-section">
                    <span className="umpire-label">
                      Umpire:{' '}
                      <span className="umpire-name">
                        {match.umpire || 'To Be Assigned'}
                      </span>
                    </span>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <div className="no-matches">
              {matches.length === 0 
                ? "No matches found for this tournament."
                : "No matches match the selected filters."
              }
              {matches.length > 0 && (
                <button onClick={resetFilters} className="reset-filters-btn">
                  Reset Filters
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default MatchesPage;
