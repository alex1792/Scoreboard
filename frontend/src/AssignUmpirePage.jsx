import React, { useEffect, useState } from 'react';
import './matches.css'; // 假設 CSS 放這裡
import io from 'socket.io-client';

const MatchCard = ({ match, onAssignUmpire }) => {
  const statusColorMap = {
    ended: '#4CAF50',
    ongoing: '#FFC107',
    pending: '#9E9E9E'
  };

  const statusColor = statusColorMap[match.status?.toLowerCase()] || '#ccc';

  return (
    <div className={`match-card status-${match.status?.toLowerCase()}`} data-match-id={match.match_id}>
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

      <div className="score">{match.score1} : {match.score2}</div>

      <div className="status">
        <span className={`status-badge status-${match.status?.toLowerCase()}`}
              style={{ backgroundColor: statusColor + '20', color: statusColor }}>
          {match.status?.toUpperCase()}
        </span>
      </div>

      <div className="umpire-section">
        <span className="umpire-label">
          Umpire: <span className="umpire-name">{match.umpire ? match.umpire.username : 'To Be Assigned'}</span>
        </span>
        <button className="set-umpire-btn" onClick={() => onAssignUmpire(match.id)}>Assign Umpire</button>
      </div>
    </div>
  );
};

const MatchesPage = ({ initialMatches = [], socketUrl = 'http://127.0.0.1:5001/scoreboard' }) => {
  const [matches, setMatches] = useState(initialMatches);

  useEffect(() => {
    const socket = io(socketUrl, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 3000
    });

    socket.on('connect', () => {
      console.log('WebSocket connected:', socket.id);
    });

    socket.on('match_update', (data) => {
      setMatches(prevMatches =>
        prevMatches.map(match =>
          match.match_id === data.match_id
            ? {
                ...match,
                score1: data.score1,
                score2: data.score2,
                status: data.match_status,
                umpire: { username: data.umpire_name }
              }
            : match
        )
      );
    });

    socket.on('connect_error', (err) => {
      console.error('Connection error:', err.message);
    });

    return () => {
      socket.disconnect();
    };
  }, [socketUrl]);

  const handleAssignUmpire = async (matchId) => {
    const umpireId = prompt('Please insert Umpire User ID:');
    if (!umpireId || umpireId.trim() === '') return;

    try {
      const response = await fetch(`/assign_umpire/${matchId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ umpire_id: umpireId })
      });

      if (response.ok) {
        const data = await response.json();
        setMatches(prevMatches =>
          prevMatches.map(match =>
            match.id === matchId
              ? {
                  ...match,
                  umpire: { username: data.umpire_name }
                }
              : match
          )
        );
      } else {
        alert('Assign failed');
      }
    } catch (err) {
      console.error('Fetch error:', err);
    }
  };

  return (
    <BaseLayout>
      <div className="container">
        <h1 className="page-title">All Matches</h1>
        <div className="matches-grid">
          {matches.map(match => (
            <MatchCard key={match.id} match={match} onAssignUmpire={handleAssignUmpire} />
          ))}
        </div>
      </div>
    </BaseLayout>
  );
};

export default MatchesPage;