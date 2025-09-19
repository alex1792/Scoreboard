import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { fetchInfoFromBackend } from '../../api/api';
import { getTournamentUrl, getTournamentBracketUrl } from '../../config/urls';
import { useMatchInfoListener } from '../../api/socketService';
import MatchCard from '../../components/match/MatchCard'; // 添加這行
import '../../styles/pages/tournament/TournamentBracketPage.css';

const TournamentBracketPage = () => {
  const { tournamentId } = useParams();
  const [tournament, setTournament] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [animatingMatchId, setAnimatingMatchId] = useState(null);
  
  // 添加分類狀態
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedGroup, setSelectedGroup] = useState('all');
  
  // WebSocket 連接引用
  const socketRef = useRef(null);

  useEffect(() => {
    loadTournamentData();
  }, [tournamentId]);

  // 使用 WebSocket 監聽器 - 修復更新邏輯
  useMatchInfoListener(socketRef, { 
    setMatches: (updater) => {
      setMatches(prev => {
        if (typeof updater === 'function') {
          const updated = updater(prev);
          // 只更新比賽狀態相關字段，保留 bracket 定位信息
          return updated.map(newMatch => {
            const existingMatch = prev.find(m => m.id === newMatch.id);
            if (existingMatch) {
              return {
                ...existingMatch, // 保留所有原有數據
                // 只更新狀態相關字段
                status: newMatch.status,
                score1: newMatch.score1,
                score2: newMatch.score2,
                winner: newMatch.winner,
                player1: newMatch.player1 || existingMatch.player1, // 允許更新參賽者名稱
                player2: newMatch.player2 || existingMatch.player2, // 允許更新參賽者名稱
                player1_game_won: newMatch.player1_game_won,
                player2_game_won: newMatch.player2_game_won,
                game1_score1: newMatch.game1_score1,
                game1_score2: newMatch.game1_score2,
                game2_score1: newMatch.game2_score1,
                game2_score2: newMatch.game2_score2,
                game3_score1: newMatch.game3_score1,
                game3_score2: newMatch.game3_score2,
                current_game: newMatch.current_game,
                umpire: newMatch.umpire,
                umpire_id: newMatch.umpire_id
              };
            }
            return newMatch;
          });
        }
        return updater;
      });
    }, 
    setAnimatingMatchId 
  });

  const loadTournamentData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // console.log('🔄 開始載入錦標賽數據...');
      
      // 載入錦標賽資訊
      const tournamentResponse = await fetchInfoFromBackend(getTournamentUrl(tournamentId));
      
      if (tournamentResponse.status === 'success') {
        setTournament(tournamentResponse.data);
        // console.log('✅ 錦標賽資訊載入成功:', tournamentResponse.data);
      } else {
        // console.error('❌ Tournament API error:', tournamentResponse.message);
        setError(tournamentResponse.message || 'Failed to load tournament');
        return;
      }

      // 載入比賽資訊 - 確保獲取最新的賽程進度
      const matchesResponse = await fetchInfoFromBackend(getTournamentBracketUrl(tournamentId));
      
      if (matchesResponse.status === 'success') {
        const matchesData = matchesResponse.matches || [];
        // console.log('✅ 比賽資訊載入成功，共', matchesData.length, '場比賽');
        
        // 調試：檢查第一場比賽的數據結構
        if (matchesData.length > 0) {
          // console.log('🔍 第一場比賽數據結構:', matchesData[0]);
          // console.log('📊 比賽狀態統計:', {
          //   pending: matchesData.filter(m => m.status === 'Pending').length,
          //   ongoing: matchesData.filter(m => m.status === 'Ongoing').length,
          //   finished: matchesData.filter(m => m.status === 'Finished').length
          // });
        }
        
        setMatches(matchesData);
      } else {
        // console.error('❌ Matches API error:', matchesResponse.message);
        setMatches([]);
      }
    } catch (error) {
      // console.error('❌ Error loading tournament data:', error);
      setError('Failed to load tournament data');
    } finally {
      setLoading(false);
    }
  };

  // 獲取所有可用的分類和組別
  const getAvailableCategories = () => {
    const categories = new Set();
    const groups = new Set();
    
    matches.forEach(match => {
      const eventName = match.event_name || match.category;
      const groupName = match.group_name || match.group;
      
      if (eventName) categories.add(eventName);
      if (groupName) groups.add(groupName);
    });
    
    return {
      categories: Array.from(categories).sort(),
      groups: Array.from(groups).sort()
    };
  };

  // 過濾比賽數據
  const getFilteredMatches = () => {
    return matches.filter(match => {
      const eventName = match.event_name || match.category;
      const groupName = match.group_name || match.group;
      
      const categoryMatch = selectedCategory === 'all' || eventName === selectedCategory;
      const groupMatch = selectedGroup === 'all' || groupName === selectedGroup;
      
      return categoryMatch && groupMatch;
    });
  };

  // 分組比賽數據 - 使用過濾後的數據
  const groupMatchesByFormat = () => {
    const filteredMatches = getFilteredMatches();
    const eliminationMatches = {};
    const roundRobinMatches = {};

    filteredMatches.forEach(match => {
      const eventName = match.event_name || match.category;
      const groupName = match.group_name || match.group;
      const formatType = match.format_type || match.format;
      
      const key = `${eventName}-${groupName}`;
      
      if (formatType === 'elimination') {
        if (!eliminationMatches[key]) {
          eliminationMatches[key] = [];
        }
        eliminationMatches[key].push(match);
      } else if (formatType === 'round_robin') {
        if (!roundRobinMatches[key]) {
          roundRobinMatches[key] = [];
        }
        roundRobinMatches[key].push(match);
      }
    });

    return { eliminationMatches, roundRobinMatches };
  };

  // 計算 bracket 總高度 - 確保容器有足夠高度
  const calculateBracketHeight = (matchesByRound) => {
    const MATCH_HEIGHT = 120;
    const MATCH_SPACING = 120;
    const TOTAL_MATCH_SPACE = MATCH_HEIGHT + MATCH_SPACING;
    
    const firstRoundMatches = matchesByRound[1] || [];
    const firstRoundCount = firstRoundMatches.length;
    
    if (firstRoundCount > 0) {
      return (firstRoundCount - 1) * TOTAL_MATCH_SPACE + MATCH_HEIGHT;
    }
    
    return 600; // 默認高度
  };

  // 渲染單個比賽方塊 - 修正勝場數位置
  const renderMatchBox = (match) => {
    // 勝者判斷邏輯
    const getWinnerInfo = () => {
      if (match.status !== 'Finished' || !match.winner) {
        return { player1Winner: false, player2Winner: false };
      }
      
      const isByeMatch = match.player1 === 'BYE' || match.player2 === 'BYE';
      
      if (isByeMatch) {
        if (match.player1 === 'BYE') {
          return { player1Winner: false, player2Winner: true };
        } else if (match.player2 === 'BYE') {
          return { player1Winner: true, player2Winner: false };
        }
      }
      
      const player1Winner = match.winner === match.player1;
      const player2Winner = match.winner === match.player2;
      return { player1Winner, player2Winner };
    };

    const { player1Winner, player2Winner } = getWinnerInfo();

    // 修改分數顯示邏輯 - 修復狀態判斷
    const getScoreDisplay = () => {
      if (match.status === 'Finished') {
        // 比賽結束時顯示總局數勝負
        return {
          score1: match.player1_game_won || 0,
          score2: match.player2_game_won || 0,
          showGames: true
        };
      } else if (match.status === 'Ongoing') {
        // 比賽進行中顯示當前局分數
        return {
          score1: match.score1 || 0,
          score2: match.score2 || 0,
          showGames: false
        };
      } else {
        // 其他狀態（Pending 等）不顯示分數
        return {
          score1: 0,
          score2: 0,
          showGames: false
        };
      }
    };

    const { score1, score2, showGames } = getScoreDisplay();

    // 檢查是否為 BYE match
    const isByeMatch = match.player1 === 'BYE' || match.player2 === 'BYE';
    // 修復：只有 Ongoing 和 Finished 狀態才顯示分數
    const shouldShowScore = (match.status === 'Ongoing' || match.status === 'Finished') && !isByeMatch;

    // 調試：檢查勝場數數據
    // console.log(`🔍 Match ${match.id} 勝場數數據:`, {
    //   status: match.status,
    //   player1_game_won: match.player1_game_won,
    //   player2_game_won: match.player2_game_won,
    //   score1,
    //   score2,
    //   showGames
    // });

    return (
      <div className={`match-box ${animatingMatchId === match.id ? 'animate-update' : ''}`}>
        <div className={`player player1 ${player1Winner ? 'winner' : ''}`}>
          <span className="player-text">
            {player1Winner && <span className="winner-crown">👑</span>}
            {match.player1 || 'TBD'}
            {shouldShowScore && (
              <span className="score-inline">
                ({score1}{showGames && 'games'})
              </span>
            )}
          </span>
        </div>
        <div className={`player player2 ${player2Winner ? 'winner' : ''}`}>
          <span className="player-text">
            {player2Winner && <span className="winner-crown">👑</span>}
            {match.player2 || 'TBD'}
            {shouldShowScore && (
              <span className="score-inline">
                ({score2}{showGames && ' games'})
              </span>
            )}
          </span>
        </div>
      </div>
    );
  };

  // 渲染發送連接線 - 添加 data-round 屬性
  const renderOutgoingConnections = (match) => (
    match.connections && match.connections.map((connection, index) => (
      <div 
        key={`${match.id}-connection-${index}`}
        className={`bracket-connection ${connection.position}`}
        data-round={match.round}
        data-target-match={connection.match_id}
      />
    ))
  );

  // 移除 renderIncomingConnections 函數，完全依賴後端的 connections 數據

  // 渲染單個比賽 - 添加 WebSocket 更新處理
  const renderMatch = (match) => {
    // 簡化的調試信息
    // if (match.round === 3) {
    //   console.log(`🔍 Round 3 Match ${match.id}:`);
    //   console.log(`   - bracket_position: ${match.bracket_position}`);
    //   console.log(`   - match_number: ${match.match_number}`);
    //   console.log(`   - connections:`, match.connections);
    // }
    
    // 確保位置值是整數
    const topPosition = Math.round(match.bracket_position || 0);
    
    return (
      <div 
        key={match.id} 
        className="bracket-match"
        data-round={match.round}
        style={{
          position: 'absolute',
          top: `${topPosition}px`,
          left: 0,
          right: 0,
          zIndex: 2
        }}
      >
        {renderMatchBox(match)}
        {renderOutgoingConnections(match)}
      </div>
    );
  };

  // 渲染單個輪次 - 恢復高度設置，但確保不限制滾動
  const renderRound = (round, roundMatches, totalHeight) => {
    const sortedMatches = roundMatches.sort((a, b) => (a.match_number || 0) - (b.match_number || 0));
    
    return (
      <div key={round} className="bracket-round">
        <h4>Round {round}</h4>
        <div 
          className="bracket-matches"
          style={{ 
            height: `${totalHeight}px`,
            position: 'relative',
            overflow: 'visible'
          }}
        >
          {sortedMatches.map(renderMatch)}
        </div>
      </div>
    );
  };

  // 渲染淘汰賽 bracket - 恢復 totalHeight 參數
  const renderEliminationBracket = (matches, category, group) => {
    // 按輪次分組
    const matchesByRound = matches.reduce((acc, match) => {
      const round = match.round || 1;
      if (!acc[round]) acc[round] = [];
      acc[round].push(match);
      return acc;
    }, {});

    const totalHeight = calculateBracketHeight(matchesByRound);

    return (
      <div key={`${category}-${group}`} className="elimination-bracket">
        <h3>{category} - Group {group} (Elimination)</h3>
        <div className="bracket-container">
          {Object.entries(matchesByRound).map(([round, roundMatches]) => 
            renderRound(round, roundMatches, totalHeight)
          )}
        </div>
      </div>
    );
  };

  // 渲染循環賽表格 - 改用 MatchCard 組件
  const renderRoundRobinTable = (matches, category, group) => {
    // 收集所有參賽者
    const participants = new Set();
    matches.forEach(match => {
      if (match.player1) participants.add(match.player1);
      if (match.player2) participants.add(match.player2);
    });
    
    // 計算每個參賽者的統計數據
    const playerStats = {};
    Array.from(participants).forEach(player => {
      playerStats[player] = {
        name: player,
        wins: 0,
        losses: 0,
        points: 0,
        matchesPlayed: 0
      };
    });
    
    // 統計比賽結果
    matches.forEach(match => {
      if (match.status === 'Finished' && match.score1 !== undefined && match.score2 !== undefined) {
        const player1 = match.player1;
        const player2 = match.player2;
        
        if (player1 && player2) {
          playerStats[player1].matchesPlayed++;
          playerStats[player2].matchesPlayed++;
          
          if (match.score1 > match.score2) {
            playerStats[player1].wins++;
            playerStats[player1].points += 1; // winning, get 1 point
            playerStats[player2].losses += 1;
          } else if (match.score2 > match.score1) {
            playerStats[player2].wins++;
            playerStats[player2].points += 1; // winning, get 1 point
            playerStats[player1].losses += 1;
          } else {
            // 平局
            playerStats[player1].points += 1;
            playerStats[player2].points += 1;
          }
        }
      }
    });
    
    // 排序（按積分、勝場數、淨勝分）
    const sortedPlayers = Object.values(playerStats).sort((a, b) => {
      if (b.points !== a.points) return b.points - a.points;
      if (b.wins !== a.wins) return b.wins - a.wins;
      return b.wins - a.wins; // 可以添加淨勝分計算
    });
    
    return (
      <div className="round-robin-section">
        <h3>{category} - Group {group} (Round Robin)</h3>
        
        {/* 積分表 */}
        <div className="ranking-table">
          <h4>Standings</h4>
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Win</th>
                <th>Loss</th>
                <th>Matches Played</th>
                <th>Points</th>
              </tr>
            </thead>
            <tbody>
              {sortedPlayers.map((player, index) => (
                <tr key={player.name} className={index < 2 ? 'top-rank' : ''}>
                  <td>{index + 1}</td>
                  <td>{player.name}</td>
                  <td>{player.wins}</td>
                  <td>{player.losses}</td>
                  <td>{player.matchesPlayed}</td>
                  <td>{player.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* 比賽記錄 - 改用 MatchCard 組件 */}
        <div className="match-details">
          <h4>Match Results</h4>
          <div className="matches-grid">
            {matches.map((match) => (
              <MatchCard
                key={match.id}
                match={match}
                animating={animatingMatchId === match.id}
                className="round-robin-match-card"
                isClickable={true}
                enableWebSocket={true}
              />
            ))}
          </div>
        </div>
      </div>
    );
  };

  // 渲染分類導航
  const renderCategoryNavigation = () => {
    const { categories, groups } = getAvailableCategories();
    
    return (
      <div className="category-navigation">
        <div className="filter-section">
          <div className="filter-group">
            <label htmlFor="category-select">Event:</label>
            <select 
              id="category-select"
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="category-select"
            >
              <option value="all">All Events</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="group-select">Group:</label>
            <select 
              id="group-select"
              value={selectedGroup} 
              onChange={(e) => setSelectedGroup(e.target.value)}
              className="group-select"
            >
              <option value="all">All Groups</option>
              {groups.map(group => (
                <option key={group} value={group}>
                  {group}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="filter-info">
          <span className="filter-summary">
            Showing: {selectedCategory === 'all' ? 'All Events' : selectedCategory} - {selectedGroup === 'all' ? 'All Groups' : selectedGroup}
          </span>
          <span className="match-count">
            ({getFilteredMatches().length} matches)
          </span>
        </div>
      </div>
    );
  };

  // 渲染頁面內容
  const renderContent = () => {
    const { eliminationMatches, roundRobinMatches } = groupMatchesByFormat();
    const filteredMatches = getFilteredMatches();

    return (
      <div className="bracket-content">
        {/* 分類導航 */}
        {renderCategoryNavigation()}
        
        {/* 沒有比賽時的提示 */}
        {filteredMatches.length === 0 && (
          <div className="no-matches-filtered">
            <p>No matches found for the selected filters.</p>
            <button 
              onClick={() => {
                setSelectedCategory('all');
                setSelectedGroup('all');
              }}
              className="clear-filters-btn"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* 淘汰賽部分 */}
        {Object.keys(eliminationMatches).length > 0 && (
          <div className="elimination-section">
            <h2>Elimination Matches</h2>
            {Object.entries(eliminationMatches).map(([key, matches]) => {
              const [category, group] = key.split('-');
              return renderEliminationBracket(matches, category, group);
            })}
          </div>
        )}

        {/* 循環賽部分 */}
        {Object.keys(roundRobinMatches).length > 0 && (
          <div className="round-robin-section">
            <h2>Round Robin Matches</h2>
            {Object.entries(roundRobinMatches).map(([key, matches]) => {
              const [category, group] = key.split('-');
              return renderRoundRobinTable(matches, category, group);
            })}
          </div>
        )}

        {Object.keys(eliminationMatches).length === 0 && 
         Object.keys(roundRobinMatches).length === 0 && 
         filteredMatches.length > 0 && (
          <div className="no-matches">
            <p>No matches found for this tournament.</p>
          </div>
        )}
      </div>
    );
  };

  // 載入狀態
  if (loading) {
    return <div className="loading">Loading tournament bracket...</div>;
  }

  // 錯誤狀態
  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  // 錦標賽不存在
  if (!tournament) {
    return <div className="no-tournament">Tournament not found</div>;
  }

  return (
    <div className="tournament-bracket-page">
      <div className="page-header">
        <h1>{tournament.name} - Tournament Bracket</h1>
        <div className="tournament-info">
          <span>Status: {tournament.status || 'TBD'}</span>
          <span>Location: {tournament.location || 'TBD'}</span>
        </div>
      </div>
      {renderContent()}
    </div>
  );
};

export default TournamentBracketPage;