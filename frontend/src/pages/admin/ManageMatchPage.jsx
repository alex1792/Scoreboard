import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import '../../styles/pages/match/matches.css'; 
import { useMatchInfoListener } from '../../api/socketService';
import { useFetchMatchInfo } from '../../api/api';
import { deleteMatch } from '../../api/api';
import MatchCard from '../../components/match/MatchCard';

const ManageMatchPage = () => {
  const [matches, setMatches] = useState([]);
  const [animatingMatchId, setAnimatingMatchId] = useState(null);
  const socketRef = useRef(null);
  
  // fetch match info from backend
  useFetchMatchInfo(setMatches);
  
  // match info listener
  useMatchInfoListener(socketRef, { setMatches, setAnimatingMatchId });
  
  // Handle match deletion with local state update
  const handleDeleteMatch = async (matchId) => {
    const success = await deleteMatch(matchId);
    if (success) {
      setMatches(prev => prev.filter(match => match.id !== matchId));
    }
  };

  return (
    <>
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">Manage Matches</h1>
          <Link to="/create-match" className="create-match-link">
            <button className="create-match-btn">Create New Match</button>
          </Link>
        </div>
        <div className="matches-grid">
          {matches.map(match => (
            <MatchCard
              key={match.id}
              match={match}
              onDelete={handleDeleteMatch}
              showDeleteButton={true}
              showPredecessors={true}
            />
          ))}
        </div>
      </div>
    </>
  );
};

export default ManageMatchPage;
