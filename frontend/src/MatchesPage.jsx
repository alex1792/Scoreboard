import React, { useEffect } from 'react';
import io from 'socket.io-client';
import BaseLayout from './BaseLayout';

const Matches = ({ matches = [] }) => {
  useEffect(() => {
    const socket = io('http://127.0.0.1:5001/scoreboard', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000
    });

    socket.on('connect', () => {
      console.log('WebSocket 已連接！Socket ID:', socket.id);
    });

    socket.on('match_update', (data) => {
      console.log('收到比赛更新:', data);
      const matchCard = document.querySelector(`.match-card[data-match-id="${data.match_id}"]`);
      if (matchCard) {
        // 更新比分
        const scoreElement = matchCard.querySelector('.score');
        if (scoreElement) scoreElement.textContent = `${data.score1} : ${data.score2}`;

        // 更新裁判名稱
        const umpireNameElement = matchCard.querySelector('.umpire-name');
        if (umpireNameElement) umpireNameElement.textContent = data.umpire_name || 'To Be Assigned';

        // 更新狀態標籤與樣式
        const statusBadge = matchCard.querySelector('.status-badge');
        if (statusBadge && data.match_status) {
          statusBadge.textContent = data.match_status.toUpperCase();
          statusBadge.className = `status-badge status-${data.match_status.toLowerCase()}`;
          matchCard.className = `match-card status-${data.match_status.toLowerCase()}`;
        }

        matchCard.style.transition = 'transform 0.2s ease';
        matchCard.style.transform = 'scale(1.05)';
        setTimeout(() => {
          matchCard.style.transform = 'scale(1)';
        }, 200);
      }
    });

    socket.on('connect_error', (err) => {
      console.error('連接錯誤:', err.message);
      setTimeout(() => socket.connect(), 5000);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const getStatusColor = (status) => {
    const colorMap = {
      ended: '#4CAF50',
      ongoing: '#FFC107',
      pending: '#9E9E9E'
    };
    return {
      backgroundColor: `${colorMap[status.toLowerCase()]}20`,
      color: colorMap[status.toLowerCase()]
    };
  };

  return (
    // <BaseLayout>
    <>
      <div className="container">
        <h1 className="page-title">All Matches</h1>

        <div className="matches-grid">
          {matches.length > 0 ? (
            matches.map((match) => (
              <a
                key={match.id}
                href="/scoreboard"
                className="match-card-link"
              >
                <div
                  className={`match-card status-${match.status.toLowerCase()}`}
                  data-match-id={match.id}
                >
                  <div className="match-id">#{match.id}</div>

                  <div className="players">
                    <div className="player">
                      <div className="player-name">{match.player1.name}</div>
                      <small>ID: {match.player1_id}</small>
                    </div>

                    <div className="vs">vs</div>

                    <div className="player">
                      <div className="player-name">{match.player2.name}</div>
                      <small>ID: {match.player2_id}</small>
                    </div>
                  </div>

                  <div className="score">
                    {match.score1} : {match.score2}
                  </div>

                  <div className="status">
                    <span
                      className={`status-badge status-${match.status.toLowerCase()}`}
                      style={getStatusColor(match.status)}
                    >
                      {match.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="umpire-section">
                    <span className="umpire-label">
                      Umpire:{' '}
                      <span className="umpire-name">
                        {match.umpire?.username || 'To Be Assigned'}
                      </span>
                    </span>
                  </div>
                </div>
              </a>
            ))
          ) : (
            <div className="no-matches">目前沒有賽事</div>
          )}
        </div>
      </div>
    </>
    // </BaseLayout>
  );
};

export default Matches;
