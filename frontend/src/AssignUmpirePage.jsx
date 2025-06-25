import { useState, useRef } from 'react';
import './matches.css'; 
import { useMatchInfoListener } from './api/socketService';
import { useFetchMatchInfo } from './api/api';
import { assignUmpire } from './api/api';
import { deleteMatch } from './api/api';


const MatchCard = ({ match, onAssignUmpire, onDeleteMatch }) => {
  const statusColorMap = {
    ended: '#4CAF50',
    ongoing: '#FFC107',
    pending: '#9E9E9E'
  };

  const statusColor = statusColorMap[match.status?.toLowerCase()] || '#ccc';

  return (
    <div className={`match-card status-${match.status?.toLowerCase()}`} data-match-id={match.match_id} style={{ position: 'relative' }}>
      <button
        className="close-btn"
        aria-label="Close"
        onClick={() => onDeleteMatch(match.id)}
        type="button"
      >
        &times;
      </button>
      <div className="match-header">
        <div className="match-id">#{match.id}</div>
        <div className="match-category">{match.category}</div>
      </div>
      
      <div className="players">
        <div className="player">
          <div className="player-name">{match.player1}</div>
          {/* <small>ID: {match.player1_id}</small> */}
        </div>
        <div className="vs">vs</div>
        <div className="player">
          <div className="player-name">{match.player2}</div>
          {/* <small>ID: {match.player2_id}</small> */}
        </div>
      </div>

      <div className="score">{match.score1} : {match.score2}</div>

      <div className="status">
        <span
          className={`status-badge status-${match.status?.toLowerCase()}`}
          style={{ backgroundColor: statusColor + '20', color: statusColor }}
        >
          {match.status?.toUpperCase()}
        </span>
      </div>

      <div className="umpire-section">
        <span className="umpire-label">
          Umpire: <span className="umpire-name">
            {typeof match.umpire === 'object' ? match.umpire.username : (match.umpire || 'To Be Assigned')}
          </span>
        </span>
        <button className="set-umpire-btn" onClick={() => onAssignUmpire(match.id)}>Assign Umpire</button>
      </div>
    </div>
  );
};

const AssignUmpirePage = () => {
  const [matches, setMatches] = useState([]);
  const [animatingMatchId, setAnimatingMatchId] = useState(null);
  const socketRef = useRef(null);
  
  // fetch match info from backend
  useFetchMatchInfo(setMatches);
  
  // match info listener
  useMatchInfoListener(socketRef, { setMatches, setAnimatingMatchId });

  // Handle match deletion with local state update
  const handleDeleteMatch = async (matchId) => {
    const success = await deleteMatch(matchId);
    if (success) {
      // Update local state immediately without waiting for socket event
      setMatches(prev => prev.filter(match => match.id !== matchId));
    }
  };

  return (
    <>
      <div className="container">
        <h1 className="page-title">All Matches</h1>
        <div className="matches-grid">
          {matches.map(match => (
            <MatchCard key={match.id} match={match} onAssignUmpire={assignUmpire} onDeleteMatch={handleDeleteMatch} />
          ))}
        </div>
      </div>
    </>
  );
};

export default AssignUmpirePage;
