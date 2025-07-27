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
  const [matchStatus, setMatchStatus] = useState('');
  const [umpireId, setUmpireId] = useState('');
  
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

  return (
    <>
      <div className="scoreboard-container">
        {/* Match Info */}
        <div className="match-info">
          <p>
            <strong>{player1Name}</strong> vs <strong>{player2Name}</strong>
          </p>
          <p>
            Match Status: <span id="match-status">{matchStatus}</span>
          </p>
          <p>Match ID: {matchId}</p>
          {/* 調試信息 */}
          <p>Umpire ID: {umpireId || 'Not assigned'}</p>
          <p>Current User ID: {currentUser?.id || 'Not logged in'}</p>
          <p>User Role: {currentUser?.role || 'No role'}</p>
        </div>

        {/* Scores */}
        <div className="scores">
          <div className="score-container">
            <span id="player1-score" className="score">{score1}</span>
            <span className="separator">-</span>
            <span id="player2-score" className="score">{score2}</span>
          </div>
        </div>

        {/* Umpire Controls */}
        {canEditScore && (
          <>
            <div className="button-container">
              <div className="button-group">
                <button className="btn btn-add" onClick={() => handleScoreChange('Player1', 1)}>
                  Player1 +1
                </button>
                <button className="btn btn-minus" onClick={() => handleScoreChange('Player1', -1)}>
                  Player1 -1
                </button>
              </div>

              <div className="button-group">
                <button className="btn btn-add" onClick={() => handleScoreChange('Player2', 1)}>
                  Player2 +1
                </button>
                <button className="btn btn-minus" onClick={() => handleScoreChange('Player2', -1)}>
                  Player2 -1
                </button>
              </div>
            </div>

            <div className="match-status-container">
              <button className="btn btn-status" onClick={handleStatusToggle}>
                {matchStatus === 'Scheduled' && 'Start Match'}
                {matchStatus === 'Ongoing' && 'End Match'}
                {matchStatus === 'Finished' && 'Restart Match'}
              </button>
            </div>
          </>
        )}

        {/* 如果沒有權限，顯示提示信息 */}
        {!canEditScore && currentUser && (
          <div style={{ 
            textAlign: 'center', 
            padding: '1rem', 
            background: '#f8f9fa', 
            borderRadius: '8px',
            marginTop: '1rem'
          }}>
            <p>You don't have permission to edit this match.</p>
            <p>User ID: {currentUser.id} | Umpire ID: {umpireId}</p>
          </div>
        )}
      </div>
    </>
  );
};

export default Scoreboard;