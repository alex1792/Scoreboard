import React, { useState } from 'react';


const CreateMatch = () => {
  const [player1Username, setPlayer1Username] = useState('');
  const [player2Username, setPlayer2Username] = useState('');

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
          player2_username: player2Username
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
        <div className="create-form-container">
          <h1>Create New Match</h1>
          <form onSubmit={handleSubmit}>
              <label htmlFor="player1_username">Player1 Username</label>
              <input
              id="player1_username"
              name="player1_username"
              value={player1Username}
              onChange={(e) => setPlayer1Username(e.target.value)}
              required
              />

              <label htmlFor="player2_username">Player2 Username</label>
              <input
              id="player2_username"
              name="player2_username"
              value={player2Username}
              onChange={(e) => setPlayer2Username(e.target.value)}
              required
              />

              <input type="submit" value="Create Match" />
          </form>
        </div>
    </>
  );
};

export default CreateMatch;