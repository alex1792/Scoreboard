import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import io from 'socket.io-client';
import './matches.css';
// import BaseLayout from './BaseLayout';

const MatchesPage = () => {
  const [matches, setMatches] = useState([]);
  const socketRef = useRef(null);

  // 從後端 API 取得 matches 資料
  useEffect(() => {
    fetch('http://localhost:5001/api/matches')
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        setMatches(data.data);
      }
    })
    .catch(err => console.error('獲取賽事失敗:', err));
  }, []);
  

  // WebSocket 連線與事件監聽
  useEffect(() => {
    // 如果已有連線，先斷開
    if (socketRef.current) {
      socketRef.current.disconnect();
    }

    // 建立新連線
    socketRef.current = io('http://localhost:5001/scoreboard', {
      // path: '/scoreboard/socket.io',
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000
    });

    socketRef.current.on('connect', () => {
      // console.log('WebSocket 已連接！Socket ID:', socketRef.current.id);
    });

    socketRef.current.on('match_update', (data) => {
      console.log('收到比赛更新:', data);
      // 確保 data 包含 match_id
      const matchCard = document.querySelector(`.match-card[data-match-id="${data.id}"]`);
      if (matchCard) {
        // 更新比分
        const scoreElement = matchCard.querySelector('.score');
        if (scoreElement) scoreElement.textContent = `${data.score1} : ${data.score2}`;

        // 更新裁判名稱
        const umpireNameElement = matchCard.querySelector('.umpire-name');
        if (umpireNameElement) umpireNameElement.textContent = data.umpire || 'To Be Assigned';

        // 更新狀態標籤與樣式
        const statusBadge = matchCard.querySelector('.status-badge');
        if (statusBadge && data.status) {
          statusBadge.textContent = data.status.toUpperCase();
          statusBadge.className = `status-badge status-${data.status.toLowerCase()}`;
          matchCard.className = `match-card status-${data.status.toLowerCase()}`;
        }

        // 動畫效果
        matchCard.style.transition = 'transform 0.2s ease';
        matchCard.style.transform = 'scale(1.05)';
        setTimeout(() => {
          matchCard.style.transform = 'scale(1)';
        }, 200);
      }
    });

    socketRef.current.on('connect_error', (err) => {
      // console.error('連接錯誤:', err.message);
    });

    // 清理函數
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []); // 空依賴陣列，只執行一次

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

  // console.log('Matches type: ', typeof(matches));

  return (
    <>
      <div className="container">
        <h1 className="page-title">All Matches</h1>

        <div className="matches-grid">
          {matches.length > 0 ? (
            matches.map((match) => (
              <Link
                key={match.id}
                to={`/matches/${match.id}`}
                className="match-card-link"
              >
                <div
                  className={`match-card status-${match.status.toLowerCase()}`}
                  data-match-id={match.id}
                >
                  <div className="match-id">#{match.id}</div>

                  <div className="players">
                    <div className="player">
                      <div className="player-name">{match.player1}</div>
                      <small>ID: {match.player1_id}</small>
                    </div>

                    <div className="vs">vs</div>

                    <div className="player">
                      <div className="player-name">{match.player2}</div>
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
                        {match.umpire || 'To Be Assigned'}
                      </span>
                    </span>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <div className="no-matches">目前沒有賽事</div>
          )}
        </div>
      </div>
    </>
  );
};

export default MatchesPage;
