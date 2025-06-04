import React, { useState } from 'react';
import BaseLayout from './BaseLayout';

const CreateForm = () => {
  const [player1Username, setPlayer1Username] = useState('');
  const [player2Username, setPlayer2Username] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('/create_match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          player1_username: player1Username,
          player2_username: player2Username
        })
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
    <BaseLayout>
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

            <input type="submit" value="Update Role" />
        </form>
        </div>
    </BaseLayout>
  );
};

export default CreateForm;