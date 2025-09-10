import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import MatchCard from '../../components/match/MatchCard';
import '../../styles/pages/tournament/PlayerHistoryPage.css';
import { useMatchInfoListener } from '../../api/socketService';

const PlayerHistoryPage = () => {
  const { tournamentId } = useParams();
  const [playerName, setPlayerName] = useState('');
  const [playerHistory, setPlayerHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // WebSocket 相關狀態
  const [matches, setMatches] = useState([]);
  const [animatingMatchId, setAnimatingMatchId] = useState(null);
  const socketRef = useRef(null);

  // 頁面層級管理 WebSocket
  useMatchInfoListener(socketRef, { setMatches, setAnimatingMatchId });

  const handleSearch = async () => {
    if (!playerName.trim()) {
      setError('請輸入選手姓名');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/tournaments/${tournamentId}/player-history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ player_name: playerName })
      });

      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.status === 'success') {
        setPlayerHistory(data.data);
      } else {
        setError(data.message || '查詢失敗');
      }
    } catch (err) {
      setError('網路錯誤，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  // 移除 convertToMatchCardFormat 函數，直接使用 match 資料
  // 當 WebSocket 更新 matches 時，同步更新 playerHistory 中的相關比賽
  useEffect(() => {
    if (playerHistory && matches.length > 0) {
      const updatedMatchHistory = playerHistory.match_history.map(historyMatch => {
        const updatedMatch = matches.find(m => m.id === historyMatch.match_id);
        return updatedMatch ? { ...historyMatch, ...updatedMatch } : historyMatch;
      });
      
      setPlayerHistory(prev => ({
        ...prev,
        match_history: updatedMatchHistory
      }));
    }
  }, [matches, playerHistory]);

  if (loading) {
    return <div className="loading">Loading player history...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="player-history-page">
      <div className="page-header">
        <h1>Player History</h1>
        <p>Tournament ID: {tournamentId}</p>
      </div>

      <div className="search-section">
        <div className="search-form">
          <input
            type="text"
            placeholder="輸入選手姓名"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button 
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? '查詢中...' : '查詢'}
          </button>
        </div>
      </div>

      {playerHistory && (
        <div className="player-history-content">
          {/* 選手資訊和統計 */}
          <div className="player-info">
            <h2>{playerHistory.player_name}</h2>
            <div className="statistics">
              <div className="stat-item">
                <span className="stat-label">Total Matches</span>
                <span className="stat-value">{playerHistory.statistics.total_matches}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Finished</span>
                <span className="stat-value">{playerHistory.statistics.completed_matches}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Win</span>
                <span className="stat-value win">{playerHistory.statistics.wins}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Loss</span>
                <span className="stat-value loss">{playerHistory.statistics.losses}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Winning Rate</span>
                <span className="stat-value">{playerHistory.statistics.win_rate}%</span>
              </div>
            </div>
          </div>

          {/* 比賽歷史 - 使用 MatchCard */}
          <div className="matches-section">
            <h3>比賽記錄</h3>
            {playerHistory.match_history.length === 0 ? (
              <div className="no-matches">沒有找到比賽記錄</div>
            ) : (
              <div className="matches-grid">
                {playerHistory.match_history.map((match) => (
                  <MatchCard
                    key={match.id}
                    match={match}  // 直接使用，不需要轉換
                    isClickable={false}
                    showDeleteButton={false}
                    showAssignUmpireButton={false}
                    showPredecessors={false}
                    enableWebSocket={false}
                    animating={animatingMatchId === match.id}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerHistoryPage;