import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import io from 'socket.io-client';
import '../../styles/pages/match/scoreboard.css';

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

  // 1. Fetch match data from backend API
  useEffect(() => {
    fetch(`http://localhost:5001/api/matches/${matchId}`)
      .then(res => res.json())
      .then(result => {
        if (result.status === 'success') {
          setPlayer1Name(result.data.player1);
          setPlayer2Name(result.data.player2);
          setScore1(result.data.score1);
          setScore2(result.data.score2);
          setMatchStatus(result.data.status);
          setUmpireId(result.data.umpire_id);
          
          console.log('Match data:', result.data);
        }
      });
  }, [matchId]);

  // 2. socket.io listener for score updates
  useEffect(() => {
    let isConnecting = false;

    const connectSocket = () => {
      if (isConnecting) return;
      isConnecting = true;

      if (socketRef.current) {
        socketRef.current.disconnect();
      }

      socketRef.current = io('http://127.0.0.1:5001/scoreboard', {
        transports: ['websocket'],
        reconnection: true,
        reconnectionDelay: 3000,
      });

      socketRef.current.on('connect', () => {
        console.log('Socket connected');
        isConnecting = false;
      });

      // 添加 match_update 事件監聽器
      socketRef.current.on('match_update', (data) => {
        console.log('收到分數更新:', data);
        
        // 檢查是否是當前比賽的更新
        if (data.id === Number(matchId)) {
          console.log('更新當前比賽分數:', data);
          setScore1(data.score1);
          setScore2(data.score2);
          setMatchStatus(data.status);
        }
      });

      socketRef.current.on('connect_error', () => {
        console.log('Connection failed, retrying...');
        isConnecting = false;
      });
    };

    connectSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
      isConnecting = false;
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
        url: `http://localhost:5001/api/matches/${Number(matchId)}/score`,
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

  const getNextStatus = (current) => {
    if(current === "Scheduled") return "Ongoing";
    if(current === "Ongoing") return "Finished";
    if(current === "Finished") return "Scheduled";
    return "Ongoing";
  };

  const handleStatusToggle = async () => {
    const token = localStorage.getItem('access_token');
    const nextStatus = getNextStatus(matchStatus);
    try {
      const res = await fetch(`http://localhost:5001/api/matches/${matchId}/score`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          action_type: 'change_status',
          new_status: nextStatus
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

        {/* 控制按鈕 - 網格布局 */}
        {canEditScore && (
          <div className="control-section">
            <div className="score-controls">
              <div className="player-controls">
                <h4 className="player-label">Player 1</h4>
                <div className="button-row">
                  <button className="btn btn-minus" onClick={() => handleScoreChange('Player1', -1)}>
                    -1
                  </button>
                  <button className="btn btn-add" onClick={() => handleScoreChange('Player1', 1)}>
                    +1
                  </button>
                </div>
              </div>

              <div className="player-controls">
                <h4 className="player-label">Player 2</h4>
                <div className="button-row">
                  <button className="btn btn-minus" onClick={() => handleScoreChange('Player2', -1)}>
                    -1
                  </button>
                  <button className="btn btn-add" onClick={() => handleScoreChange('Player2', 1)}>
                    +1
                  </button>
                </div>
              </div>
            </div>

            {/* 比賽狀態控制 */}
            <div className="match-controls">
              <button className="btn btn-status" onClick={handleStatusToggle}>
                {matchStatus === 'Scheduled' && '▶ Start Match'}
                {matchStatus === 'Ongoing' && '⏹ End Match'}
                {matchStatus === 'Finished' && '🔄 Restart Match'}
              </button>
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