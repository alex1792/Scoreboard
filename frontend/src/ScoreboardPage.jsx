import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import './scoreboard.css'; // 假設 CSS 放在同目錄下
import BaseLayout from './BaseLayout';

const Scoreboard = ({
  player1Name,
  player2Name,
  score1: initialScore1,
  score2: initialScore2,
  matchStatus: initialStatus,
  matchId,
  currentUser,
  umpireId,
}) => {
  const [score1, setScore1] = useState(initialScore1);
  const [score2, setScore2] = useState(initialScore2);
  const [matchStatus, setMatchStatus] = useState(initialStatus);

  useEffect(() => {
    const socket = io('http://127.0.0.1:5001/scoreboard', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000,
    });

    socket.on('connect', () => {
      console.log('WebSocket 已連接！Socket ID:', socket.id);
    });

    socket.on('match_update', (data) => {
      console.log('收到分數更新:', data);
      if (data.match_id === matchId) {
        setScore1(data.score1);
        setScore2(data.score2);
        setMatchStatus(data.match_status);
      }
    });

    socket.on('connect_error', (err) => {
      console.error('連接錯誤:', err.message);
      setTimeout(() => socket.connect(), 5000);
    });

    return () => {
      socket.disconnect();
    };
  }, [matchId]);

  const handleScoreChange = async (player, delta) => {
    await fetch('/update_score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        action_type: 'update_score',
        player,
        score: delta,
        match_id: matchId,
      }),
    });
  };

  const handleStatusToggle = async () => {
    await fetch('/update_score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        action_type: 'change_status',
        match_id: matchId,
        new_status: matchStatus === 'ongoing' ? 'finished' : 'ongoing',
      }),
    });
  };

  return (
    <BaseLayout>
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
        {currentUser?.is_authenticated && currentUser.id === umpireId && (
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
    </BaseLayout>
  );
};

export default Scoreboard;