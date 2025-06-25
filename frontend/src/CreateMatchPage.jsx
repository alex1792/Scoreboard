import { useState } from 'react';
import './matches.css';

const CreateMatch = () => {
  const [player1Username, setPlayer1Username] = useState('');
  const [player2Username, setPlayer2Username] = useState('');
  const [category, setCategory] = useState('');

  const categories = [
    "Men's Single",
    "Men's Doubles",
    "Women's Singles",
    "Women's Doubles",
    "Mixed Doubles"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem('access_token');
      const requestInfo = {
        url: `http://localhost:5001/api/matches/create_match`,
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
         },
        body: JSON.stringify({ 
          player1_username: player1Username,
          player2_username: player2Username,
          category: category
        })
      };

      const response = await fetch(requestInfo.url, {
        method: 'POST',
        headers: requestInfo.headers,
        body: requestInfo.body
      });

      if (response.ok) {
        alert('Match created successfully!');
        setPlayer1Username('');
        setPlayer2Username('');
        setCategory('');
      } else {
        alert('Failed to create match.');
      }
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

              <div className="score">0 : 0</div>

              <div className="status">
                <span className="status-badge status-pending">
                  PENDING
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