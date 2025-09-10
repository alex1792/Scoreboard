import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './MatchCard.css';
import { useMatchInfoListener } from '../../api/socketService';

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
  animating = false,
  enableWebSocket = false,
}) => {
  const [currentMatch, setCurrentMatch] = useState(match);
  const [isAnimating, setIsAnimating] = useState(animating);
  const socketRef = useRef(null);

  // 當外部 match prop 更新時，同步內部狀態
  useEffect(() => {
    setCurrentMatch(match);
  }, [match]);

  // 創建一個只包含當前 match 的數組
  const [matches, setMatches] = useState([match]);

  // 處理比賽更新的函數
  const handleMatchUpdate = (updatedMatch) => {
    if (updatedMatch.id === currentMatch.id) {
      setCurrentMatch(updatedMatch);
      setIsAnimating(true);
      
      // 動畫結束後重置
      setTimeout(() => {
        setIsAnimating(false);
      }, 1000);
    }
  };

  // 處理動畫的函數
  const handleAnimatingMatchId = (matchId) => {
    if (matchId === currentMatch.id) {
      setIsAnimating(true);
      setTimeout(() => setIsAnimating(false), 1000);
    }
  };

  // 使用 WebSocket Hook
  useMatchInfoListener(socketRef, { 
    setMatches: enableWebSocket ? (prev) => {
      // prev 是一個 matches 數組，我們需要找到更新的 match
      const updatedMatch = prev.find(m => m.id === currentMatch.id);
      if (updatedMatch) {
        handleMatchUpdate(updatedMatch);
      }
      return prev; // 返回更新後的數組
    } : () => {}, // 如果禁用 WebSocket，提供空函數
    setAnimatingMatchId: enableWebSocket ? handleAnimatingMatchId : () => {}
  });

  // 清理 WebSocket 連接
  useEffect(() => {
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const statusColorMap = {
    ended: '#4CAF50',
    ongoing: '#FFC107',
    pending: '#9E9E9E'
  };

  const statusColor = statusColorMap[currentMatch.status?.toLowerCase()] || '#ccc';

  // 修正勝者判斷邏輯 - 處理 BYE match
  const getWinnerInfo = () => {
    if (currentMatch.status !== 'Finished' || !currentMatch.winner) {
      return { player1Winner: false, player2Winner: false };
    }
    
    // 檢查是否為 BYE match
    const isByeMatch = currentMatch.player1 === 'BYE' || currentMatch.player2 === 'BYE';
    
    if (isByeMatch) {
      // BYE match 的勝者判斷
      if (currentMatch.player1 === 'BYE') {
        return { player1Winner: false, player2Winner: true };
      } else if (currentMatch.player2 === 'BYE') {
        return { player1Winner: true, player2Winner: false };
      }
    }
    
    // 一般比賽的勝者判斷
    const player1Winner = currentMatch.winner === currentMatch.player1;
    const player2Winner = currentMatch.winner === currentMatch.player2;
    return { player1Winner, player2Winner };
  };

  const { player1Winner, player2Winner } = getWinnerInfo();

  // 修改分數顯示邏輯 - 從各局分數計算遊戲勝負
  const getScoreDisplay = () => {
    if (currentMatch.status === 'Finished') {
      // 如果 player1_game_won 和 player2_game_won 為 0，嘗試從各局分數計算
      let gameWon1 = currentMatch.player1_game_won || 0;
      let gameWon2 = currentMatch.player2_game_won || 0;
      
      // 如果遊戲勝負為 0，嘗試從各局分數計算
      if (gameWon1 === 0 && gameWon2 === 0) {
        // 檢查各局分數
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
      // 比賽進行中顯示當前局分數
      return {
        score1: currentMatch.player1_score || 0,
        score2: currentMatch.player2_score || 0,
        showGames: false
      };
    } else {
      // 其他狀態（Pending 等）不顯示分數
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
  // 修復：只有 Ongoing 和 Finished 狀態才顯示分數
  const shouldShowScore = (currentMatch.status === 'Ongoing' || currentMatch.status === 'Finished') && !isByeMatch;

  // 修正：遊戲歷史顯示邏輯
  const renderGameHistory = () => {
    const games = [];
    
    // 檢查每一局是否有分數
    if (currentMatch.game1_score1 > 0 || currentMatch.game1_score2 > 0) {
      games.push(`G1: ${currentMatch.game1_score1}-${currentMatch.game1_score2}`);
    }
    
    if (currentMatch.game2_score1 > 0 || currentMatch.game2_score2 > 0) {
      games.push(`G2: ${currentMatch.game2_score1}-${currentMatch.game2_score2}`);
    }
    
    if (currentMatch.game3_score1 > 0 || currentMatch.game3_score2 > 0) {
      games.push(`G3: ${currentMatch.game3_score1}-${currentMatch.game3_score2}`);
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

  // 調試信息
  // console.log('MatchCard Debug:', {
  //   id: currentMatch.id,
  //   status: currentMatch.status,
  //   winner: currentMatch.winner,
  //   player1: currentMatch.player1,
  //   player2: currentMatch.player2,
  //   player1Winner,
  //   player2Winner,
  //   score1,
  //   score2,
  //   showGames
  // });

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
              {currentMatch.player1}
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
              {currentMatch.player2}
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
          className={`status-badge status-${currentMatch.status?.toLowerCase()}`}
          style={{ backgroundColor: statusColor + '20', color: statusColor }}
        >
          {currentMatch.status?.toUpperCase()}
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
  if (isClickable) {
    return (
      <Link to={`/matches/${currentMatch.id}`} className="match-card-link">
        {cardContent}
      </Link>
    );
  }

  return cardContent;
};

export default MatchCard;
