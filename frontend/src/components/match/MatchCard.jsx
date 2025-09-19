import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './MatchCard.css';
import { updateMatchScore } from '../../api/api';

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
  onDelete = () => {}, // 添加默認值
  onAssignUmpire = () => {}, // 添加默認值
  showDeleteButton = false,
  showAssignUmpireButton = false,
  showPredecessors = false,
  className = '',
  isClickable = false,
  animating = false,
  enableWebSocket = false,
  canEditScore = false,
  onScoreUpdate,
}) => {
  const [currentMatch, setCurrentMatch] = useState(match);
  const [isAnimating, setIsAnimating] = useState(animating);
  
  // 編輯狀態管理
  const [editingScore, setEditingScore] = useState(false);
  const [tempScore1, setTempScore1] = useState(0);
  const [tempScore2, setTempScore2] = useState(0);
  const [isUpdating, setIsUpdating] = useState(false);

  // 當外部 match prop 更新時，同步內部狀態
  useEffect(() => {
    setCurrentMatch(match);
    
    // 根據比賽狀態設置正確的分數顯示
    if (match.status === 'Finished') {
      setTempScore1(match.player1_game_won || 0);
      setTempScore2(match.player2_game_won || 0);
    } else if (match.status === 'Ongoing') {
      // 優先使用 score1/score2（來自 Socket.IO 更新），如果沒有則使用 player1_score/player2_score
      const score1 = match.score1 !== undefined ? match.score1 : (match.player1_score || 0);
      const score2 = match.score2 !== undefined ? match.score2 : (match.player2_score || 0);
      setTempScore1(score1);
      setTempScore2(score2);
    } else {
      setTempScore1(0);
      setTempScore2(0);
    }
  }, [match]);

  // 處理動畫
  useEffect(() => {
    if (animating) {
      setIsAnimating(true);
      setTimeout(() => setIsAnimating(false), 1000);
    }
  }, [animating]);

  // 開始編輯分數
  const startEditingScore = () => {
    if (!canEditScore || currentMatch.status !== 'Ongoing') return;
    
    setEditingScore(true);
    setTempScore1(currentMatch.player1_score || 0);
    setTempScore2(currentMatch.player2_score || 0);
  };

  // 取消編輯分數
  const cancelEditingScore = () => {
    setEditingScore(false);
    if (currentMatch.status === 'Finished') {
      setTempScore1(currentMatch.player1_game_won || 0);
      setTempScore2(currentMatch.player2_game_won || 0);
    } else if (currentMatch.status === 'Ongoing') {
      setTempScore1(currentMatch.player1_score || 0);
      setTempScore2(currentMatch.player2_score || 0);
    } else {
      setTempScore1(0);
      setTempScore2(0);
    }
  };

  // 保存分數
  const saveScore = async () => {
    if (isUpdating) return;
    
    setIsUpdating(true);
    try {
      await updateMatchScore(currentMatch.id, tempScore1, tempScore2);
      setEditingScore(false);
      
      if (onScoreUpdate) {
        onScoreUpdate(currentMatch.id, tempScore1, tempScore2);
      }
    } catch (error) {
      console.error('Failed to update score:', error);
      alert('Failed to update score. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  // 處理鍵盤事件
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      saveScore();
    } else if (e.key === 'Escape') {
      cancelEditingScore();
    }
  };

  // 勝者判斷邏輯
  const getWinnerInfo = () => {
    if (currentMatch.status !== 'Finished' || !currentMatch.winner) {
      return { player1Winner: false, player2Winner: false };
    }
    
    const isByeMatch = currentMatch.player1 === 'BYE' || currentMatch.player2 === 'BYE';
    
    if (isByeMatch) {
      if (currentMatch.player1 === 'BYE') {
        return { player1Winner: false, player2Winner: true };
      } else {
        return { player1Winner: true, player2Winner: false };
      }
    }
    
    const player1Winner = currentMatch.winner === currentMatch.player1;
    const player2Winner = currentMatch.winner === currentMatch.player2;
    
    return { player1Winner, player2Winner };
  };

  const { player1Winner, player2Winner } = getWinnerInfo();

  // 分數顯示邏輯
  const getScoreDisplay = () => {
    if (currentMatch.status === 'Finished') {
      let gameWon1 = currentMatch.player1_game_won || 0;
      let gameWon2 = currentMatch.player2_game_won || 0;
      
      if (gameWon1 === 0 && gameWon2 === 0) {
        if (currentMatch.game1_score1 !== undefined && currentMatch.game1_score2 !== undefined) {
          if (currentMatch.game1_score1 > currentMatch.game1_score2) {
            gameWon1++;
          } else if (currentMatch.game1_score1 < currentMatch.game1_score2) {
            gameWon2++;
          }
        }
        
        if (currentMatch.game2_score1 !== undefined && currentMatch.game2_score2 !== undefined) {
          if (currentMatch.game2_score1 > currentMatch.game2_score2) {
            gameWon1++;
          } else if (currentMatch.game2_score1 < currentMatch.game2_score2) {
            gameWon2++;
          }
        }
        
        if (currentMatch.game3_score1 !== undefined && currentMatch.game3_score2 !== undefined) {
          if (currentMatch.game3_score1 > currentMatch.game3_score2) {
            gameWon1++;
          } else if (currentMatch.game3_score1 < currentMatch.game3_score2) {
            gameWon2++;
          }
        }
      }
      
      return {
        score1: gameWon1,
        score2: gameWon2,
        showGames: true
      };
    } else if (currentMatch.status === 'Ongoing') {
      // 優先使用 score1/score2（來自 Socket.IO 更新）
      const score1 = currentMatch.score1 !== undefined ? currentMatch.score1 : (currentMatch.player1_score || 0);
      const score2 = currentMatch.score2 !== undefined ? currentMatch.score2 : (currentMatch.player2_score || 0);
      
      return {
        score1: score1,
        score2: score2,
        showGames: false
      };
    } else {
      return {
        score1: 0,
        score2: 0,
        showGames: false
      };
    }
  };

  const { score1, score2, showGames } = getScoreDisplay();

  // 檢查是否為 BYE match
  const isByeMatch = currentMatch.player1 === 'BYE' || currentMatch.player2 === 'BYE';
  const shouldShowScore = (currentMatch.status === 'Ongoing' || currentMatch.status === 'Finished') && !isByeMatch;

  // 遊戲歷史顯示
  const renderGameHistory = () => {
    const games = [];
    
    if (currentMatch.game1_score1 > 0 || currentMatch.game1_score2 > 0) {
      games.push(`G1: ${currentMatch.game1_score1}-${currentMatch.game1_score2}`);
    }
    
    if (currentMatch.game2_score1 > 0 || currentMatch.game2_score2 > 0) {
      games.push(`G2: ${currentMatch.game2_score1}-${currentMatch.game2_score2}`);
    }
    
    if (currentMatch.game3_score1 > 0 || currentMatch.game3_score2 > 0) {
      games.push(`G3: ${currentMatch.game3_score1}-${currentMatch.game3_score2}`);
    }
    
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

  // 渲染可編輯的分數
  const renderEditableScore = (playerScore, setTempScore, isPlayer1) => {
    if (editingScore && currentMatch.status === 'Ongoing') {
      return (
        <input
          type="number"
          min="0"
          max="99"
          value={playerScore}
          onChange={(e) => setTempScore(parseInt(e.target.value) || 0)}
          onKeyDown={handleKeyDown}
          onBlur={saveScore}
          className="score-input"
          autoFocus={isPlayer1}
          disabled={isUpdating}
        />
      );
    }
    
    return (
      <span 
        className={`score-display ${canEditScore && currentMatch.status === 'Ongoing' ? 'editable' : ''}`}
        onClick={canEditScore && currentMatch.status === 'Ongoing' ? startEditingScore : undefined}
        title={canEditScore && currentMatch.status === 'Ongoing' ? 'Click to edit score' : ''}
      >
        {playerScore}
        {showGames && <span className="score-label">games</span>}
      </span>
    );
  };

  const statusColorMap = {
    ended: '#4CAF50',
    ongoing: '#FFC107',
    pending: '#9E9E9E'
  };

  const statusColor = statusColorMap[currentMatch.status?.toLowerCase()] || '#ccc';

  const cardContent = (
    <div
      className={`match-card status-${currentMatch.status?.toLowerCase()} ${isAnimating ? 'animating' : ''} ${className}`}
      data-match-id={currentMatch.id}
      style={showDeleteButton ? { position: 'relative' } : {}}
    >
      {showDeleteButton && (
        <button
          className="close-btn"
          aria-label="Close"
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDelete(currentMatch.id); }}
          type="button"
        >
          &times;
        </button>
      )}
      
      <div className="match-header">
        <div className="match-id">#{currentMatch.id}</div>
        <div className="match-category">
          {currentMatch.round && currentMatch.match_number ? (
            `${currentMatch.category}-${currentMatch.group} : Round ${currentMatch.round} - Match ${currentMatch.match_number}`
          ) : (
            `${currentMatch.category}-${currentMatch.group}`
          )}
        </div>
      </div>
      
      {showPredecessors && currentMatch.prev_match1_id && (
        <div className="match-predecessors">
          <small>Winner of Match #{currentMatch.prev_match1_id} vs Winner of Match #{currentMatch.prev_match2_id}</small>
        </div>
      )}
      
      {renderGameHistory()}
      
      <div className="players-vertical">
        <div className={`player-row ${player1Winner ? 'winner' : ''}`}>
          <div className="player-info">
            <span className="player-name">
              {player1Winner && <span className="winner-crown">👑</span>}
              {currentMatch.player1}
            </span>
          </div>
          {shouldShowScore && (
            <div className="player-score">
              {renderEditableScore(tempScore1, setTempScore1, true)}
            </div>
          )}
        </div>
        
        <div className={`player-row ${player2Winner ? 'winner' : ''}`}>
          <div className="player-info">
            <span className="player-name">
              {player2Winner && <span className="winner-crown">👑</span>}
              {currentMatch.player2}
            </span>
          </div>
          {shouldShowScore && (
            <div className="player-score">
              {renderEditableScore(tempScore2, setTempScore2, false)}
            </div>
          )}
        </div>
      </div>

      <div className="status">
        <span
          className={`status-badge status-${currentMatch.status?.toLowerCase()}`}
          style={{ backgroundColor: statusColor + '20', color: statusColor }}
        >
          {currentMatch.status?.toUpperCase()}
        </span>
      </div>

      <div className="court-section">
        <span className="court-label">
          Court: <span className="court-number">
            {currentMatch.court_number || currentMatch.court || 'TBD'}
          </span>
        </span>
      </div>

      <div className="umpire-section">
        <span className="umpire-label">
          Umpire: <span className="umpire-name">
            {typeof currentMatch.umpire === 'object' ? currentMatch.umpire.username : (currentMatch.umpire || 'To Be Assigned')}
          </span>
        </span>
        {showAssignUmpireButton && (
          <button className="set-umpire-btn" onClick={() => onAssignUmpire(currentMatch.id)}>
            Assign Umpire
          </button>
        )}
      </div>
    </div>
  );

  // 如果可點擊，包裝在 Link 中
  if (isClickable && !editingScore) {
    return (
      <Link to={`/matches/${currentMatch.id}`} className="match-card-link">
        {cardContent}
      </Link>
    );
  }

  return cardContent;
};

export default MatchCard;
