import { useState } from 'react';

const ManageMatch = () => {
  const [matchId, setMatchId] = useState('');

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/update_match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ match_id: matchId })
      });

      if (response.ok) {
        alert('Match updated successfully!');
        setMatchId('');
      } else {
        alert('Failed to update match.');
      }
    } catch (err) {
      console.error('Update Error:', err);
      alert('Error updating match.');
    }
  };

  const handleClearAll = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5001/api/matches/clear_all_match', {
        method: 'POST', 
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        alert('All matches cleared!');
      } else {
        alert('Failed to clear matches.');
      }
    } catch (err) {
      console.error('Clear Error:', err);
      alert('Error clearing matches.');
    }
  };

  return (
    // <BaseLayout>
    <>
        <div className="manage-match-container">
        <h1>Update Match</h1>

        <form onSubmit={handleUpdate}>
            <label htmlFor="match_id">Match ID</label>
            <input
            id="match_id"
            name="match_id"
            value={matchId}
            onChange={(e) => setMatchId(e.target.value)}
            required
            />
            <input type="submit" value="Update Role" />
        </form>

        <form onSubmit={handleClearAll}>
            <input
            type="submit"
            value="Clear All Matches"
            style={{ backgroundColor: 'red', color: 'white', marginTop: '1em' }}
            />
        </form>
        </div>
    </>
    // {/* </BaseLayout> */}
  );
};

export default ManageMatch;