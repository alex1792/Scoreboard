import React, { useEffect, useState, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { AuthContext } from './AuthContext'; 
import io from 'socket.io-client';
import './scoreboard.css';
// import BaseLayout from './BaseLayout';

const Scoreboard = ({currentUser}) => {
  // parent conponent沒有pass scoreboard的資料 所以這裡要再fetch一次
  const { matchId } = useParams();
  const [player1Name, setPlayer1Name] = useState('');
  const [player2Name, setPlayer2Name] = useState('');
  const [score1, setScore1] = useState(0);
  const [score2, setScore2] = useState(0);
  const [matchStatus, setMatchStatus] = useState('');
  const [umpireId, setUmpireId] = useState('');

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
        }
      });
  }, [matchId]);

  // 2. socket.io listner for score updates
  useEffect(() => {
    // create a new socket connection
    const socket = io('http://127.0.0.1:5001/scoreboard', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000,
    });

    // listen for match updates
    socket.on('match_update', (data) => {
      console.log('Receive score update:', data);
      // when checking data.id and matchId, make sure to convert them to numbers
      if (Number(data.id) === Number(matchId)) {
        setScore1(data.score1);
        setScore2(data.score2);
        setMatchStatus(data.match_status);
      }
    });

    // handle connection error
    socket.on('connect_error', (err) => {
      console.error('連接錯誤:', err.message);
      setTimeout(() => socket.connect(), 5000);
    });

    return () => {
      socket.disconnect();
    };
  }, [matchId]);


  const handleScoreChange = async (player, delta) => {
    const token = localStorage.getItem('access_token');
    
    // check if user is logged in or not, if not, alert user to login 
    if (!token) {
      alert('not logged in or token is lost, please login again');
      return;
    }

    // At this point, user is logged in, so we can proceed to update score
    try {
      // request info
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
      }
    } catch (err) {
      console.error('error：', err);
      alert('connection error, please try again later');
    }
  };

  const handleStatusToggle = async () => {
    const token = localStorage.getItem('access_token');
    try {
      const res = await fetch(`http://localhost:5001/api/matches/${matchId}/score`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          action_type: 'change_status',
          new_status: matchStatus === 'ongoing' ? 'finished' : 'ongoing'
        }),
      });
      
      const data = await res.json();
      console.log('狀態更新回應：', data);
      
      if (!res.ok) {
        alert(`狀態更新失敗: ${data.message || res.status}`);
      }
    } catch (err) {
      console.error('狀態更新錯誤：', err);
      alert('網路錯誤，請稍後再試');
    }
  };

// console.log('currentUser:', currentUser, 'umpireId:', umpireId);

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
        {currentUser && Number(currentUser.id) === Number(umpireId) && (
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
                {matchStatus === 'ongoing' ? 'End Match' : 'Start Match'}
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default Scoreboard;