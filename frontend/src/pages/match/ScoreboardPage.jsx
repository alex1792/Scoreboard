import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useMatchInfoListener } from '../../api/socketService'; // 添加這行
import '../../styles/pages/match/scoreboard.css';
import { getMatchUrl, getMatchScoreUrl, getMatchNextGameUrl, getMatchEndMatchUrl } from '../../config/urls';
import { io } from 'socket.io-client'; // 新增這行
import { updateMatchScore } from '../../api/api'; // 新增 import

const Scoreboard = () => {
  const { currentUser } = useAuth();
  const { matchId } = useParams();
  const [player1Name, setPlayer1Name] = useState('');
  const [player2Name, setPlayer2Name] = useState('');
  const [score1, setScore1] = useState(0);
  const [score2, setScore2] = useState(0);
  const [matchStatus, setMatchStatus] = useState('Scheduled');
  const [umpireId, setUmpireId] = useState(null);
  const socketRef = useRef(null);

  // 新增三局制相關的 state
  const [currentGame, setCurrentGame] = useState(1);
  const [gamesWon, setGamesWon] = useState({ player1: 0, player2: 0 });

  // 添加暫停狀態
  const [isPaused, setIsPaused] = useState(false);

  // 新增：編輯狀態管理
  const [editingScore, setEditingScore] = useState(false);
  const [tempScore1, setTempScore1] = useState(0);
  const [tempScore2, setTempScore2] = useState(0);
  const [isUpdating, setIsUpdating] = useState(false);

  // 1. Fetch match data from backend API
  useEffect(() => {
    fetch(`${getMatchUrl(matchId)}`)
      .then(res => res.json())
      .then(result => {
        if (result.status === 'success') {
          setPlayer1Name(result.data.player1);
          setPlayer2Name(result.data.player2);
          setScore1(result.data.score1);
          setScore2(result.data.score2);
          setMatchStatus(result.data.status);
          setUmpireId(result.data.umpire_id);
          
          // 新增：處理三局制數據
          setCurrentGame(result.data.current_game || 1);
          setGamesWon({
            player1: result.data.player1_game_won || 0,
            player2: result.data.player2_game_won || 0
          });
          
          // console.log('Match data:', result.data);
        }
      });
  }, [matchId]);

  // 在 useEffect 中同步 tempScore 和 score
  useEffect(() => {
    setTempScore1(score1);
    setTempScore2(score2);
  }, [score1, score2]);

  // 2. 專門的WebSocket監聽器
  useEffect(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }

    const socketUrl = process.env.NODE_ENV === 'production' 
        ? 'https://itsyuhungkung.sc-heduling.com'
        : 'http://localhost:5001';

    console.log('🔗 Connecting to Socket.IO:', `${socketUrl}/scoreboard`);

    socketRef.current = io(`${socketUrl}/scoreboard`, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000,
      path: '/socket.io/'
    });

    socketRef.current.on('connect', () => {
      console.log('✅ Scoreboard WebSocket connected! Socket ID:', socketRef.current.id);
      console.log('Namespace:', socketRef.current.nsp);
    });

    socketRef.current.on('connect_error', (err) => {
      console.error('❌ Scoreboard WebSocket connection error:', err.message);
      console.error('Error details:', err);
    });

    socketRef.current.on('disconnect', (reason) => {
      console.log('🔌 Scoreboard WebSocket disconnected:', reason);
    });

    socketRef.current.on('match_update', (data) => {
      console.log(' Scoreboard received match_update:', data);
      console.log('Current matchId:', matchId, 'Type:', typeof matchId);
      console.log('Data ID:', data.id, 'Type:', typeof data.id);
      
      // 檢查是否是當前比賽的更新
      if (data.id === Number(matchId)) {
        console.log('✅ Updating local state with:', { score1: data.score1, score2: data.score2 });
        setScore1(data.score1);
        setScore2(data.score2);
        setMatchStatus(data.status);
        setCurrentGame(data.current_game || 1);
        setGamesWon({
          player1: data.player1_game_won || 0,
          player2: data.player2_game_won || 0
        });
      } else {
        console.log('❌ Update not for current match');
      }
    });

    return () => {
      if (socketRef.current) {
        console.log('🧹 Cleaning up Scoreboard WebSocket connection');
        socketRef.current.disconnect();
      }
    };
  }, [matchId]);

  // 修改 handleScoreChange 函數，同時更新 tempScore
  const handleScoreChange = async (player, delta) => {
    console.log('🔥 handleScoreChange called with:', { player, delta });
    
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    try {
      const res = await fetch(`${getMatchScoreUrl(Number(matchId))}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          action_type: 'update_score',
          player: player,
          score: delta
        })
      });

      const data = await res.json();

      if (!res.ok) {
        alert(`Score update failed: ${data.message || res.status}`);
      } else {
        // 同時更新 score 和 tempScore
        if (player === 'Player1') {
          const newScore = Math.max(0, score1 + delta);
          setScore1(newScore);
          setTempScore1(newScore);
        } else if (player === 'Player2') {
          const newScore = Math.max(0, score2 + delta);
          setScore2(newScore);
          setTempScore2(newScore);
        }
      }
    } catch (err) {
      console.error('Score update error:', err);
      alert('Connection error, please try again later');
    }
  };

  // 新增：下一局按鈕處理
  const handleNextGame = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    // console.log('點擊 Next Game 按鈕'); // 新增調試
    // console.log('當前 currentGame:', currentGame); // 新增調試
    // console.log('當前 gamesWon:', gamesWon); // 新增調試

    try {
      const res = await fetch(`${getMatchNextGameUrl(Number(matchId))}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await res.json();
      // console.log('Next game API 響應:', data); // 新增調試

      if (!res.ok) {
        alert(`Next game failed: ${data.message || res.status}`);
      } else {
        // console.log('Next game request sent successfully');
        // 移除手動更新，讓 Socket.IO 處理
        // setScore1(0);
        // setScore2(0);
        // setCurrentGame(currentGame + 1);
      }
    } catch (err) {
      // console.error('Next game error：', err);
      alert('connection error, please try again later');
    }
  };

  // 新增：結束比賽按鈕處理
  const handleEndMatch = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    try {
      const res = await fetch(`${getMatchEndMatchUrl(Number(matchId))}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await res.json();

      if (!res.ok) {
        alert(`End match failed: ${data.message || res.status}`);
      } else {
        // console.log('End match request sent successfully');
        setMatchStatus('Finished');
      }
    } catch (err) {
      // console.error('End match error：', err);
      alert('connection error, please try again later');
    }
  };

  // 簡化的狀態切換邏輯
  const getNextStatus = (current) => {
    if (current === "Scheduled") return "Ongoing";
    if (current === "Ongoing") return "Ongoing"; // 保持 Ongoing，不變
    if (current === "Finished") return "Scheduled";
    return "Ongoing";
  };

  // 簡化的按鈕處理
  const handleStatusToggle = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    try {
      let newStatus;
      
      if (matchStatus === 'Scheduled') {
        newStatus = 'Ongoing';
      } else if (matchStatus === 'Ongoing') {
        // 如果已經是 Ongoing，就不做任何改變
        return;
      } else if (matchStatus === 'Finished') {
        newStatus = 'Scheduled';
      }

      const res = await fetch(`${getMatchScoreUrl(Number(matchId))}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          action_type: 'change_status',
          new_status: newStatus
        }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        alert(`狀態更新失敗: ${data.message || res.status}`);
      } else {
        // console.log('Status update request sent successfully');
      }
    } catch (err) {
      console.error('狀態更新錯誤：', err);
      alert('網路錯誤，請稍後再試');
    }
  };

  // 修復 handleFinishedStatusChange 函數
  const handleFinishedStatusChange = async (newStatus) => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    // 確認對話框
    const actionText = newStatus === 'Scheduled' ? 'restart' : 'undo end match';
    const warningText = newStatus === 'Scheduled' 
      ? 'This will reset all scores and start over.' 
      : 'This will keep current scores but clear winner status.';
      
    if (!window.confirm(`Are you sure you want to ${actionText}? ${warningText}`)) {
      return;
    }

    try {
      // 使用正確的 API 端點和參數
      const res = await fetch(`${getMatchScoreUrl(Number(matchId))}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          action_type: 'change_status',
          new_status: newStatus
        }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        alert(`Status update failed: ${data.message || res.status}`);
      } else {
        console.log('Status update request sent successfully');
        console.log('Updated match data:', data.data);
        
        // 更新本地狀態
        setMatchStatus(newStatus);
        
        // 根據新狀態更新其他相關狀態
        if (newStatus === 'Scheduled') {
          // 完全重置
          setScore1(0);
          setScore2(0);
          setCurrentGame(1);
          setGamesWon({ player1: 0, player2: 0 });
        } else if (newStatus === 'Ongoing') {
          // 保留分數，但清除勝者狀態（前端不需要特別處理，因為後端已經處理了）
          console.log('Match reset to Ongoing - scores preserved, winner status cleared');
        }
        
        alert(`Match successfully ${actionText === 'restart' ? 'restarted' : 'reset to ongoing'}`);
      }
    } catch (err) {
      console.error('Status update error:', err);
      alert('Network error, please try again');
    }
  };

  // 修改：渲染 Finished 狀態的選項
  const renderFinishedOptions = () => {
    if (matchStatus === 'Finished' && canEditScore) {
      return (
        <div className="finished-options">
          <div className="finished-options-header">
            <h4>Match Finished</h4>
          </div>
          <div className="finished-options-buttons">
            <button 
              className="control-btn btn-restart"
              onClick={() => handleFinishedStatusChange('Scheduled')}
              title="Restart Match (Reset All)"
            >
              🔄 Restart Match
              <span className="button-description">Reset all scores and start over</span>
            </button>
            
            <button 
              className="control-btn btn-undo"
              onClick={() => handleFinishedStatusChange('Ongoing')}
              title="Undo End Match (Keep Scores)"
            >
              ↩️ Undo End Match
              <span className="button-description">Keep current scores and continue</span>
            </button>
          </div>
        </div>
      );
    }
    return null;
  };

  // 調試信息
  // console.log('Debug info:', {
  //   currentUser,
  //   currentUserId: currentUser?.id,
  //   umpireId,
  //   isCurrentUserUmpire: currentUser && Number(currentUser.id) === Number(umpireId),
  //   userRole: currentUser?.role
  // });

  // 新增：開始編輯分數
  const startEditingScore = () => {
    if (matchStatus !== 'Ongoing') return;
    
    setEditingScore(true);
    // 確保 tempScore 是字符串，這樣輸入框可以為空
    setTempScore1(score1.toString());
    setTempScore2(score2.toString());
  };

  // 新增：取消編輯分數
  const cancelEditingScore = () => {
    setEditingScore(false);
    setTempScore1(score1);
    setTempScore2(score2);
  };

  // 修改 saveScore 函數，確保正確更新並發送 Socket.IO 事件
  const saveScore = async () => {
    if (isUpdating) return;
    
    setIsUpdating(true);
    try {
      // 確保分數是數字
      const finalScore1 = typeof tempScore1 === 'string' ? parseInt(tempScore1) || 0 : tempScore1;
      const finalScore2 = typeof tempScore2 === 'string' ? parseInt(tempScore2) || 0 : tempScore2;
      
      console.log('Saving scores:', { finalScore1, finalScore2 });
      
      const result = await updateMatchScore(matchId, finalScore1, finalScore2);
      console.log('Save result:', result);
      
      // 更新本地狀態
      setScore1(finalScore1);
      setScore2(finalScore2);
      setTempScore1(finalScore1);
      setTempScore2(finalScore2);
      setEditingScore(false);
      
      // 確保 Socket.IO 事件被發送
      console.log('Score saved successfully, Socket.IO should broadcast the update');
      
    } catch (error) {
      console.error('Failed to update score:', error);
      alert('Failed to update score. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  // 新增：處理鍵盤事件
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      saveScore();
    } else if (e.key === 'Escape') {
      cancelEditingScore();
    }
  };

  // 修改 renderEditableScore 函數，解決輸入問題
  const renderEditableScore = (currentScore, setTempScore, isPlayer1) => {
    if (editingScore && matchStatus === 'Ongoing') {
      return (
        <input
          type="number"
          min="0"
          max="99"
          value={currentScore}
          onChange={(e) => {
            const value = e.target.value;
            // 允許空字符串，這樣用戶可以清空輸入框
            if (value === '') {
              setTempScore('');
            } else {
              const numValue = parseInt(value);
              if (!isNaN(numValue)) {
                setTempScore(numValue);
              }
            }
          }}
          onKeyDown={handleKeyDown}
          onBlur={(e) => {
            // 如果輸入為空，設為 0
            if (e.target.value === '') {
              setTempScore(0);
            }
          }}
          className="score-input"
          autoFocus={isPlayer1}
          disabled={isUpdating}
          placeholder="0"
        />
      );
    }
    
    return (
      <span 
        className={`score-number ${canEditScore && matchStatus === 'Ongoing' ? 'editable' : ''}`}
        onClick={canEditScore && matchStatus === 'Ongoing' ? startEditingScore : undefined}
        title={canEditScore && matchStatus === 'Ongoing' ? 'Click to edit score' : ''}
      >
        {currentScore}
      </span>
    );
  };

  // 改進的權限判斷
  const canEditScore = currentUser && (
    Number(currentUser.id) === Number(umpireId) || 
    currentUser.role === 'admin' ||
    currentUser.role === 'host'
  );

  const statusColorMap = {
    'Scheduled': '#9E9E9E',
    'Ongoing': '#FFC107',
    'Finished': '#4CAF50'
  };

  const statusColor = statusColorMap[matchStatus] || '#ccc';

  // 修正按鈕顯示邏輯
  const shouldShowNextGame = currentGame < 3 && matchStatus === 'Ongoing';
  const shouldShowEndMatch = matchStatus === 'Ongoing';

  return (
    <div className="scoreboard-page">
      <div className="scoreboard-card">
        {/* 簡化的 Header */}
        <div className="match-header">
          <div className="match-id">Match #{matchId}</div>
          <div className="match-status-badge">
            <span
              className={`status-badge status-${matchStatus.toLowerCase()}`}
              style={{ backgroundColor: statusColor + '20', color: statusColor }}
            >
              {matchStatus.toUpperCase()}
            </span>
          </div>
        </div>

        {/* 新增：遊戲歷史顯示 */}
        <div className="game-history">
          {/* 這裡可以顯示 game1_score1, game2_score1 等 */}
        </div>

        {/* 新增：局數勝負顯示 */}
        <div className="games-won">
          <span>Games: {gamesWon.player1} - {gamesWon.player2}</span>
        </div>

        {/* 選手姓名 - 水平排列 */}
        <div className="players-row">
          <div className="player-name">{player1Name}</div>
          <div className="vs-divider">VS</div>
          <div className="player-name">{player2Name}</div>
        </div>

        {/* 大分數顯示 - 核心焦點 */}
        <div className="score-display">
          <div className="score-container">
            <div className="score-box">
              {renderEditableScore(tempScore1, setTempScore1, true)}
            </div>
            <div className="score-separator">:</div>
            <div className="score-box">
              {renderEditableScore(tempScore2, setTempScore2, false)}
            </div>
          </div>
          
          {/* 編輯模式下的保存/取消按鈕 */}
          {editingScore && (
            <div className="score-edit-controls">
              <button 
                className="btn-save" 
                onClick={saveScore}
                disabled={isUpdating}
              >
                {isUpdating ? 'Saving...' : 'Save'}
              </button>
              <button 
                className="btn-cancel" 
                onClick={cancelEditingScore}
                disabled={isUpdating}
              >
                Cancel
              </button>
            </div>
          )}
        </div>

        {/* 控制按鈕 - 音樂播放器風格 */}
        {canEditScore && (
          <div className="control-section">
            {/* 分數控制保持不變 */}
            <div className="score-controls">
              <div className="player-controls">
                <h4 className="player-label">Player 1</h4>
                <div className="button-row">
                  <button className="btn btn-minus" onClick={() => handleScoreChange('Player1', -1)}>
                    -
                  </button>
                  <button className="btn btn-add" onClick={() => handleScoreChange('Player1', 1)}>
                    +
                  </button>
                </div>
              </div>

              <div className="player-controls">
                <h4 className="player-label">Player 2</h4>
                <div className="button-row">
                  <button className="btn btn-minus" onClick={() => handleScoreChange('Player2', -1)}>
                    -
                  </button>
                  <button className="btn btn-add" onClick={() => handleScoreChange('Player2', 1)}>
                    +
                  </button>
                </div>
              </div>
            </div>

            {/* 音樂播放器風格的控制按鈕 */}
            <div className="music-player-controls">
              <div className="control-buttons">
                {/* Start/Pause 按鈕 */}
                {matchStatus === 'Scheduled' && (
                  <button 
                    className="control-btn btn-play-pause"
                    onClick={handleStatusToggle}
                    title='Start Match'
                  >
                    ▶
                  </button>
                )}

                {/* Next Game 按鈕 - 只在進行中且未暫停時顯示 */}
                {shouldShowNextGame && (
                  <button 
                    className="control-btn btn-next"
                    onClick={handleNextGame}
                    title="Next Game"
                  >
                    ⏭
                  </button>
                )}

                {/* End Match 按鈕 - 只在進行中且未暫停時顯示 */}
                {shouldShowEndMatch && (
                  <button 
                    className="control-btn btn-stop"
                    onClick={handleEndMatch}
                    title="End Match"
                  >
                    ⏹
                  </button>
                )}
              </div>
            </div>

            {/* 新增：Finished 狀態的選項 */}
            {renderFinishedOptions()}
          </div>
        )}

        {/* 權限提示 - 簡化版本 */}
        {!canEditScore && currentUser && (
          <div className="permission-message">
            <p>You don't have permission to edit this match.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Scoreboard;