import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import MatchCard from '../../components/match/MatchCard';
import { fetchInfoFromBackend } from '../../api/api';
import { getTournamentUrl, getTournamentMatchesUrl } from '../../config/urls';
import { createMatch } from '../../api/api';
import '../../styles/pages/match/matches.css';
import { updateMatchScore } from '../../api/api';
import { useMatchInfoListener } from '../../api/socketService';

const MatchesPage = () => {
  const { tournamentId } = useParams();
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  // 狀態管理
  const [matches, setMatches] = useState([]);
  const [filteredMatches, setFilteredMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Socket.IO 相關
  const socketRef = useRef(null);
  const [animatingMatchId, setAnimatingMatchId] = useState(null);
  
  // 使用 Socket.IO hook
  useMatchInfoListener(socketRef, { 
    setMatches, 
    setAnimatingMatchId 
  });
  
  // 過濾器狀態
  const [selectedEvent, setSelectedEvent] = useState('all');
  const [selectedGroup, setSelectedGroup] = useState('all');
  const [selectedCourt, setSelectedCourt] = useState('all');
  
  // 可用選項
  const [availableEvents, setAvailableEvents] = useState([]);
  const [availableGroups, setAvailableGroups] = useState([]);
  const [eventGroups, setEventGroups] = useState({});

  // 權限檢查
  const isHostOrAdmin = currentUser && (currentUser.role === 'host' || currentUser.role === 'admin');

  // 載入比賽數據和可用選項
  useEffect(() => {
    const loadMatchesAndOptions = async () => {
      try {
        setLoading(true);
        
        // 載入比賽數據
        const result = await fetchInfoFromBackend(getTournamentMatchesUrl(tournamentId));
        
        if (result.status === 'success') {
          // 即使 result.data 是空數組也是正常的
          setMatches(result.data || []);
          
          // 從現有比賽提取可用的事件和組別
          const events = [...new Set((result.data || []).map(match => match.category))];
          const groups = [...new Set((result.data || []).map(match => match.group))];
          
          setAvailableEvents(events);
          setAvailableGroups(groups);
          
          // 建立事件與組別的對應關係
          const eventGroupMap = {};
          (result.data || []).forEach(match => {
            if (!eventGroupMap[match.category]) {
              eventGroupMap[match.category] = new Set();
            }
            eventGroupMap[match.category].add(match.group);
          });
          
          // 轉換 Set 為 Array
          Object.keys(eventGroupMap).forEach(event => {
            eventGroupMap[event] = Array.from(eventGroupMap[event]);
          });
          
          setEventGroups(eventGroupMap);
          
          // 清除之前的錯誤狀態
          setError(null);
        } else {
          // 只有在真正的錯誤時才設置錯誤狀態
          setError(result.message || 'Failed to load matches');
        }
      } catch (err) {
        console.error('Error loading matches:', err);
        // 只有在網絡錯誤或其他異常時才設置錯誤狀態
        setError('Network error. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadMatchesAndOptions();
  }, [tournamentId]);

  // 過濾比賽
  useEffect(() => {
    let filtered = [...matches];

    if (selectedEvent !== 'all') {
      filtered = filtered.filter(match => match.category === selectedEvent);
    }

    if (selectedGroup !== 'all') {
      filtered = filtered.filter(match => match.group === selectedGroup);
    }

    if (selectedCourt !== 'all') {
      filtered = filtered.filter(match => {
        const court = match.court_number || match.court;
        return court && court.toString() === selectedCourt;
      });
    }

    setFilteredMatches(filtered);
  }, [matches, selectedEvent, selectedGroup, selectedCourt]);

  // 重置過濾器
  const resetFilters = () => {
    setSelectedEvent('all');
    setSelectedGroup('all');
    setSelectedCourt('all');
  };

  // 創建比賽
  const handleCreateMatch = () => {
    navigate(`/admin/tournaments/${tournamentId}/create-match`);
  };

  // 分數更新處理
  const handleScoreUpdate = (matchId, score1, score2) => {
    console.log('Score updated:', { matchId, score1, score2 });
  };

  // 刪除比賽處理
  const handleDeleteMatch = async (matchId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/matches/${matchId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setMatches(prev => prev.filter(match => match.id !== matchId));
        setFilteredMatches(prev => prev.filter(match => match.id !== matchId));
      } else {
        alert('Failed to delete match');
      }
    } catch (error) {
      console.error('Delete match error:', error);
      alert('Failed to delete match');
    }
  };

  // 導出結果
  const handleExportResults = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/tournaments/${tournamentId}/export/results`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tournament_${tournamentId}_results.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to export results');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export results');
    }
  };

  // 渲染過濾器和控制區域（始終顯示）
  const renderFiltersAndControls = () => (
    <div className="filters-container">
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="event-filter">Event:</label>
          <select
            id="event-filter"
            value={selectedEvent}
            onChange={(e) => {
              setSelectedEvent(e.target.value);
              setSelectedGroup('all'); // 重置組別選擇
            }}
          >
            <option value="all">All Events</option>
            {/* 始終顯示常見的羽球項目 */}
            <option value="MS">MS (Men's Singles)</option>
            <option value="WS">WS (Women's Singles)</option>
            <option value="MD">MD (Men's Doubles)</option>
            <option value="WD">WD (Women's Doubles)</option>
            <option value="XD">XD (Mixed Doubles)</option>
            {/* 如果有其他自定義事件，也顯示 */}
            {availableEvents.filter(event => !['MS', 'WS', 'MD', 'WD', 'XD'].includes(event)).map(event => (
              <option key={event} value={event}>{event}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="group-filter">Group:</label>
          <select
            id="group-filter"
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
            disabled={selectedEvent === 'all'}
          >
            <option value="all">All Groups</option>
            {/* 始終顯示常見的組別 */}
            <option value="Default">Default</option>
            <option value="A">Group A</option>
            <option value="B">Group B</option>
            <option value="C">Group C</option>
            <option value="D">Group D</option>
            <option value="E">Group E</option>
            <option value="F">Group F</option>
            {/* 如果有其他自定義組別，也顯示 */}
            {selectedEvent !== 'all' && eventGroups[selectedEvent]?.filter(group => 
              !['Default', 'A', 'B', 'C', 'D', 'E', 'F'].includes(group)
            ).map(group => (
              <option key={group} value={group}>{group}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="court-filter">Court:</label>
          <select
            id="court-filter"
            value={selectedCourt}
            onChange={(e) => setSelectedCourt(e.target.value)}
          >
            <option value="all">All Courts</option>
            {Array.from({ length: 20 }, (_, i) => (
              <option key={i + 1} value={i + 1}>Court {i + 1}</option>
            ))}
          </select>
        </div>

        <button onClick={resetFilters} className="reset-filters-btn">
          Reset Filters
        </button>
      </div>

      <div className="filter-actions">
        {isHostOrAdmin && (
          <button 
            onClick={handleCreateMatch}
            className="create-match-btn"
          >
            ➕ Create New Match
          </button>
        )}
      </div>

      <div className="filter-stats">
        Showing {filteredMatches.length} of {matches.length} matches
      </div>
    </div>
  );

  // 渲染頁面內容
  const renderPageContent = () => {
    if (loading) {
      return (
        <>
          {renderFiltersAndControls()}
          <div className="loading">Loading matches...</div>
        </>
      );
    }

    if (error) {
      return (
        <>
          {renderFiltersAndControls()}
          <div className="error">Error: {error}</div>
        </>
      );
    }

    return (
      <>
        {renderFiltersAndControls()}
        
        {filteredMatches.length === 0 ? (
          <div className="no-matches">
            <div className="no-matches-content">
              <div className="no-matches-icon">🏸</div>
              <h3>No matches found</h3>
              <p>
                {matches.length === 0 
                  ? "This tournament doesn't have any matches yet. Use the filters above to see available options for creating matches."
                  : "No matches match your current filter criteria."
                }
              </p>
              {isHostOrAdmin && (
                <div className="no-matches-actions">
                  <button onClick={handleCreateMatch} className="create-first-match-btn">
                    ➕ Create Your First Match
                  </button>
                  <div className="create-match-hint">
                    <small>
                       Tip: Use the Event and Group filters above to see what types of matches you can create
                    </small>
                  </div>
                </div>
              )}
              {matches.length > 0 && (
                <button onClick={resetFilters} className="clear-filters-btn">
                  Clear Filters
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="matches-grid">
            {filteredMatches.map(match => (
              <MatchCard
                key={match.id}
                match={match}
                onDelete={handleDeleteMatch}
                showDeleteButton={isHostOrAdmin}
                showAssignUmpireButton={isHostOrAdmin}
                isClickable={true}
                enableWebSocket={false} // 改為 false，因為 MatchCard 不再處理 Socket.IO
                canEditScore={isHostOrAdmin}
                onScoreUpdate={handleScoreUpdate}
                animating={animatingMatchId === match.id} // 添加動畫效果
              />
            ))}
          </div>
        )}
      </>
    );
  };

  return (
    <div className="matches-page">
      <div className="page-header">
        <h1>Tournament Matches</h1>
        {isHostOrAdmin && (
          <button onClick={handleExportResults} className="export-btn">
            📊 Export Results
          </button>
        )}
      </div>

      {renderPageContent()}
    </div>
  );
};

export default MatchesPage;
