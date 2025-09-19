import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { createMatch} from '../../api/api';
import '../../styles/pages/match/matches.css';

const CreateMatch = () => {
  const { tournamentId } = useParams();
  
  // 單打球員
  const [player1Username, setPlayer1Username] = useState('');
  const [player2Username, setPlayer2Username] = useState('');
  
  // 雙打球員
  const [team1Player1, setTeam1Player1] = useState('');
  const [team1Player2, setTeam1Player2] = useState('');
  const [team2Player1, setTeam2Player1] = useState('');
  const [team2Player2, setTeam2Player2] = useState('');
  
  const [category, setCategory] = useState('');
  
  // 新增：Court 狀態
  const [court, setCourt] = useState('');

  const categories = [
    "Men's Single",
    "Men's Doubles",
    "Women's Singles",
    "Women's Doubles",
    "Mixed Doubles"
  ];

  // 判斷是否為雙打
  const isDoubles = category.includes('Doubles');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      let matchData;
      
      if (isDoubles) {
        // 雙打數據
        matchData = {
          team1_player1_name: team1Player1,
          team1_player2_name: team1Player2,
          team2_player1_name: team2Player1,
          team2_player2_name: team2Player2,
          category: category,
          tournament_id: tournamentId,
          court: court || null  // 添加 court 欄位
        };
      } else {
        // 單打數據
        matchData = {
          player1_username: player1Username,
          player2_username: player2Username,
          category: category,
          tournament_id: tournamentId,
          court: court || null  // 添加 court 欄位
        };
      }

      await createMatch(matchData, tournamentId);

      alert('Match created successfully!');
      
      // 清空表單
      setPlayer1Username('');
      setPlayer2Username('');
      setTeam1Player1('');
      setTeam1Player2('');
      setTeam2Player1('');
      setTeam2Player2('');
      setCategory('');
      setCourt('');  // 清空 court 欄位
    } catch (err) {
      console.error('Error:', err);
      alert('Error occurred while creating match.');
    }
  };

  return (
    <>
      <div className="container">
        <h1 className="page-title">Create New Match</h1>
        <div className="create-match-container">
          <div className="create-match-card">
            <div className="match-card status-pending">
              <div className="match-header">
                <div className="match-id">#NEW</div>
                <div className="match-category">
                  <select 
                    value={category} 
                    onChange={(e) => setCategory(e.target.value)}
                    required
                    className="category-select"
                  >
                    <option value="">Select Category</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              {isDoubles ? (
                // 雙打表單
                <div className="doubles-form">
                  <div className="team-section">
                    <h3>Team 1</h3>
                    <div className="players">
                      <div className="player">
                        <div className="player-name">
                          <input
                            type="text"
                            placeholder="Player 1"
                            value={team1Player1}
                            onChange={(e) => setTeam1Player1(e.target.value)}
                            required
                            className="player-input"
                          />
                        </div>
                      </div>
                      <div className="vs">/</div>
                      <div className="player">
                        <div className="player-name">
                          <input
                            type="text"
                            placeholder="Player 2"
                            value={team1Player2}
                            onChange={(e) => setTeam1Player2(e.target.value)}
                            required
                            className="player-input"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="vs-section">vs</div>
                  
                  <div className="team-section">
                    <h3>Team 2</h3>
                    <div className="players">
                      <div className="player">
                        <div className="player-name">
                          <input
                            type="text"
                            placeholder="Player 1"
                            value={team2Player1}
                            onChange={(e) => setTeam2Player1(e.target.value)}
                            required
                            className="player-input"
                          />
                        </div>
                      </div>
                      <div className="vs">/</div>
                      <div className="player">
                        <div className="player-name">
                          <input
                            type="text"
                            placeholder="Player 2"
                            value={team2Player2}
                            onChange={(e) => setTeam2Player2(e.target.value)}
                            required
                            className="player-input"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                // 單打表單
                <div className="players">
                  <div className="player">
                    <div className="player-name">
                      <input
                        type="text"
                        placeholder="Player 1"
                        value={player1Username}
                        onChange={(e) => setPlayer1Username(e.target.value)}
                        required
                        className="player-input"
                      />
                    </div>
                  </div>
                  <div className="vs">vs</div>
                  <div className="player">
                    <div className="player-name">
                      <input
                        type="text"
                        placeholder="Player 2"
                        value={player2Username}
                        onChange={(e) => setPlayer2Username(e.target.value)}
                        required
                        className="player-input"
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="score">0 : 0</div>

              <div className="status">
                <span className="status-badge status-pending">
                  PENDING
                </span>
              </div>

              {/* 修改：Court 下拉式選單 */}
              <div className="court-section">
                <span className="court-label">
                  Court: 
                  <select
                    value={court}
                    onChange={(e) => setCourt(e.target.value)}
                    className="court-select"
                  >
                    <option value="">Select Court</option>
                    {Array.from({ length: 20 }, (_, i) => i + 1).map(courtNum => (
                      <option key={courtNum} value={courtNum}>
                        Court {courtNum}
                      </option>
                    ))}
                  </select>
                </span>
              </div>

              <div className="umpire-section">
                <span className="umpire-label">
                  Umpire: <span className="umpire-name">To Be Assigned</span>
                </span>
                <button 
                  className="set-umpire-btn create-match-btn" 
                  onClick={handleSubmit}
                >
                  Create Match
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CreateMatch;