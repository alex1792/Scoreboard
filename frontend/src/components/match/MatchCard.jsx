import React from 'react';
import { Link } from 'react-router-dom';
import './MatchCard.css';

// If I want to dispaly the match card with different buttons, just set the parameter to true
// eg: if the admin or host has the permission to delete match, set showDeleteButton = True 
// In the following code, you can see use the code delete button to delete the match.
// <MatchCard
//   match={match}
//   onDelete={handleDeleteMatch}
//   showDeleteButton={true}
//   showPredecessors={true}
// />


const MatchCard = ({ 
  match, 
  onDelete, 
  onAssignUmpire, 
  showDeleteButton = false,
  showAssignUmpireButton = false,
  showPredecessors = true,
  isClickable = false,
  className = '',
  animating = false
}) => {
  const statusColorMap = {
    ended: '#4CAF50',
    ongoing: '#FFC107',
    pending: '#9E9E9E'
  };

  const statusColor = statusColorMap[match.status?.toLowerCase()] || '#ccc';

  const cardContent = (
    <div
      className={`match-card status-${match.status?.toLowerCase()} ${animating ? 'animating' : ''} ${className}`}
      data-match-id={match.id}
      style={showDeleteButton ? { position: 'relative' } : {}}
    >
      {showDeleteButton && (
        <button
          className="close-btn"
          aria-label="Close"
          onClick={() => onDelete(match.id)}
          type="button"
        >
          &times;
        </button>
      )}
      
      <div className="match-header">
        <div className="match-id">#{match.id}</div>
        <div className="match-category">
          {match.round && match.match_number ? (
            `${match.category}-${match.group} : Round ${match.round} - Match ${match.match_number}`
          ) : (
            `${match.category}-${match.group}`
          )}
        </div>
      </div>
      
      {showPredecessors && match.prev_match1_id && (
        <div className="match-predecessors">
          <small>Winner of Match #{match.prev_match1_id} vs Winner of Match #{match.prev_match2_id}</small>
        </div>
      )}
      
      <div className="players">
        <div className="player">
          <div className="player-name">{match.player1}</div>
        </div>
        <div className="vs">vs</div>
        <div className="player">
          <div className="player-name">{match.player2}</div>
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
        {showAssignUmpireButton && (
          <button className="set-umpire-btn" onClick={() => onAssignUmpire(match.id)}>
            Assign Umpire
          </button>
        )}
        {showDeleteButton && (
          <button className="delete-match-btn" onClick={() => onDelete(match.id)}>
            Delete Match
          </button>
        )}
      </div>
    </div>
  );

  // 如果可點擊，包裝在 Link 中
  if (isClickable) {
    return (
      <Link to={`/matches/${match.id}`} className="match-card-link">
        {cardContent}
      </Link>
    );
  }

  return cardContent;
};

export default MatchCard;
