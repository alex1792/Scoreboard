import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useMatchInfoListener } from '../../api/socketService'; // 添加這行
import '../../styles/pages/match/scoreboard.css';
import { getMatchUrl, getMatchScoreUrl, getMatchNextGameUrl, getMatchEndMatchUrl } from '../../config/urls';
import { io } from 'socket.io-client'; // 新增這行

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
          
          console.log('Match data:', result.data);
        }
      });
  }, [matchId]);

  // 2. 專門的WebSocket監聽器
  useEffect(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }

    const socketUrl = process.env.NODE_ENV === 'production' 
        ? 'https://itsyuhungkung.sc-heduling.com'
        : 'http://localhost:5001';

    socketRef.current = io(`${socketUrl}/scoreboard`, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000,
      path: '/socket.io/'
    });

    socketRef.current.on('connect', () => {
      console.log('Scoreboard WebSocket connected');
    });

    socketRef.current.on('match_update', (data) => {
      console.log('Scoreboard received update:', data);
      
      // 檢查是否是當前比賽的更新
      if (data.id === Number(matchId)) {
        setScore1(data.score1);
        setScore2(data.score2);
        setMatchStatus(data.status);
        setCurrentGame(data.current_game || 1);
        setGamesWon({
          player1: data.player1_game_won || 0,
          player2: data.player2_game_won || 0
        });
      }
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [matchId]);

  const handleScoreChange = async (player, delta) => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    try {
      const requestInfo = {
        url: `${getMatchScoreUrl(Number(matchId))}`,
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: {
          action_type: 'update_score',
          player,
          score: delta
        }
      };

      const res = await fetch(requestInfo.url, {
        method: 'POST',
        headers: requestInfo.headers,
        body: JSON.stringify(requestInfo.body)
      });

      const data = await res.json();

      if (!res.ok) {
        alert(`update failed: ${data.message || res.status}`);
      } else {
        console.log('Score update request sent successfully');
      }
    } catch (err) {
      console.error('error：', err);
      alert('connection error, please try again later');
    }
  };

  // 新增：下一局按鈕處理
  const handleNextGame = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    console.log('點擊 Next Game 按鈕'); // 新增調試
    console.log('當前 currentGame:', currentGame); // 新增調試
    console.log('當前 gamesWon:', gamesWon); // 新增調試

    try {
      const res = await fetch(`${getMatchNextGameUrl(Number(matchId))}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await res.json();
      console.log('Next game API 響應:', data); // 新增調試

      if (!res.ok) {
        alert(`Next game failed: ${data.message || res.status}`);
      } else {
        console.log('Next game request sent successfully');
        // 移除手動更新，讓 Socket.IO 處理
        // setScore1(0);
        // setScore2(0);
        // setCurrentGame(currentGame + 1);
      }
    } catch (err) {
      console.error('Next game error：', err);
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
        console.log('End match request sent successfully');
        setMatchStatus('Finished');
      }
    } catch (err) {
      console.error('End match error：', err);
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
        console.log('Status update request sent successfully');
      }
    } catch (err) {
      console.error('狀態更新錯誤：', err);
      alert('網路錯誤，請稍後再試');
    }
  };

  // 調試信息
  console.log('Debug info:', {
    currentUser,
    currentUserId: currentUser?.id,
    umpireId,
    isCurrentUserUmpire: currentUser && Number(currentUser.id) === Number(umpireId),
    userRole: currentUser?.role
  });

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
              <span className="score-number">{score1}</span>
            </div>
            <div className="score-separator">:</div>
            <div className="score-box">
              <span className="score-number">{score2}</span>
            </div>
          </div>
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

                {/* Restart Match 按鈕 - 只在比賽結束時顯示 */}
                {matchStatus === 'Finished' && (
                  <button 
                    className="control-btn btn-restart"
                    onClick={handleStatusToggle}
                    title="Restart Match"
                  >
                    ↩︎
                  </button>
                )}
              </div>
            </div>
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