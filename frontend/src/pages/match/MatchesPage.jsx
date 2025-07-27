import { useRef, useState, useContext, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMatchInfoListener } from '../../api/socketService';
import { useFetchMatchInfoByTournament } from '../../api/api';
import { useAuth } from '../../context/AuthContext';  // 改用 useAuth
import MatchCard from '../../components/match/MatchCard';
import '../../styles/pages/match/matches.css';

const MatchesPage = () => {  // 移除 currentUser prop
  const { currentUser } = useAuth();  // 使用 useAuth hook
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

  // 檢查用戶權限
  const hasAdminAccess = () => {
    return currentUser && (currentUser?.role === 'admin' || currentUser?.role === 'host' || currentUser?.role === 'organizer');
  };

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
              <MatchCard
                key={match.id}
                match={match}
                isClickable={true}
                animating={animatingMatchId === match.id}
                showPredecessors={true}
              />
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
