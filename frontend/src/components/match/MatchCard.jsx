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

  // 修正勝者判斷邏輯 - 處理 BYE match
  const getWinnerInfo = () => {
    if (match.status !== 'Finished' || !match.winner) {
      return { player1Winner: false, player2Winner: false };
    }
    
    // 檢查是否為 BYE match
    const isByeMatch = match.player1 === 'BYE' || match.player2 === 'BYE';
    
    if (isByeMatch) {
      // BYE match 的勝者判斷
      if (match.player1 === 'BYE') {
        return { player1Winner: false, player2Winner: true };
      } else if (match.player2 === 'BYE') {
        return { player1Winner: true, player2Winner: false };
      }
    }
    
    // 一般比賽的勝者判斷
    const player1Winner = match.winner === match.player1;
    const player2Winner = match.winner === match.player2;
    return { player1Winner, player2Winner };
  };

  const { player1Winner, player2Winner } = getWinnerInfo();

  // 修改分數顯示邏輯
  const getScoreDisplay = () => {
    if (match.status === 'Finished') {
      // 比賽結束時顯示總局數勝負
      return {
        score1: match.player1_game_won || 0,
        score2: match.player2_game_won || 0,
        showGames: true
      };
    } else {
      // 比賽進行中顯示當前局分數
      return {
        score1: match.score1 || 0,
        score2: match.score2 || 0,
        showGames: false
      };
    }
  };

  const { score1, score2, showGames } = getScoreDisplay();

  // 檢查是否為 BYE match
  const isByeMatch = match.player1 === 'BYE' || match.player2 === 'BYE';
  const shouldShowScore = (match.status === 'Ongoing' || match.status === 'Finished') && !isByeMatch;

  // 修正：遊戲歷史顯示邏輯
  const renderGameHistory = () => {
    const games = [];
    
    // 檢查每一局是否有分數
    if (match.game1_score1 > 0 || match.game1_score2 > 0) {
      games.push(`G1: ${match.game1_score1}-${match.game1_score2}`);
    }
    
    if (match.game2_score1 > 0 || match.game2_score2 > 0) {
      games.push(`G2: ${match.game2_score1}-${match.game2_score2}`);
    }
    
    if (match.game3_score1 > 0 || match.game3_score2 > 0) {
      games.push(`G3: ${match.game3_score1}-${match.game3_score2}`);
    }
    
    // 如果沒有任何遊戲歷史，不顯示
    if (games.length === 0) {
      return null;
    }
    
    return (
      <div className="game-history">
        {games.map((game, index) => (
          <span key={index} className="game-score">{game}</span>
        ))}
      </div>
    );
  };

  // 修正：局數勝負顯示邏輯
  // const renderGamesWon = () => {
  //   // 檢查是否有任何遊戲完成
  //   const hasGameHistory = (match.game1_score1 > 0 || match.game1_score2 > 0) ||
  //                         (match.game2_score1 > 0 || match.game2_score2 > 0) ||
  //                         (match.game3_score1 > 0 || match.game3_score2 > 0);
    
  //   if (!hasGameHistory) {
  //     return null;
  //   }
    
  //   return (
  //     <div className="games-won">
  //       <span>Games: {match.player1_game_won || 0}-{match.player2_game_won || 0}</span>
  //     </div>
  //   );
  // };

  // 調試信息
  console.log('MatchCard Debug:', {
    id: match.id,
    status: match.status,
    winner: match.winner,
    player1: match.player1,
    player2: match.player2,
    player1Winner,
    player2Winner,
    score1,
    score2,
    showGames
  });

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
      
      {/* 新增：遊戲歷史顯示 */}
      {renderGameHistory()}
      
      {/* 新增：局數勝負顯示 */}
      {/* {renderGamesWon()} */}
      
      {/* 修改玩家顯示部分 */}
      <div className="players-vertical">
        <div className={`player-row ${player1Winner ? 'winner' : ''}`}>
          <div className="player-info">
            <span className="player-name">
              {player1Winner && <span className="winner-crown">👑</span>}
              {match.player1}
            </span>
          </div>
          {shouldShowScore && (
            <div className="player-score">
              {score1}
              {showGames && <span className="score-label">games</span>}
            </div>
          )}
        </div>
        
        <div className={`player-row ${player2Winner ? 'winner' : ''}`}>
          <div className="player-info">
            <span className="player-name">
              {player2Winner && <span className="winner-crown">👑</span>}
              {match.player2}
            </span>
          </div>
          {shouldShowScore && (
            <div className="player-score">
              {score2}
              {showGames && <span className="score-label">games</span>}
            </div>
          )}
        </div>
      </div>

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
