import { useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMatchInfoListener } from '../../api/socketService';
import { useFetchMatchInfo, useFetchMatchInfoByTournament } from '../../api/api';
import '../../styles/pages/match/matches.css';

const MatchesPage = () => {
  const [matches, setMatches] = useState([]);
  const [animatingMatchId, setAnimatingMatchId] = useState(null);
  const socketRef = useRef(null);
  const { tournamentId } = useParams();

  // fetch match info from backend
  // useFetchMatchInfo(setMatches);
  useFetchMatchInfoByTournament(setMatches, tournamentId);

  // match info listener
  useMatchInfoListener(socketRef, { setMatches, setAnimatingMatchId });
  

  const getStatusColor = (status) => {
    const colorMap = {
      ended: '#4CAF50',
      ongoing: '#FFC107',
      pending: '#9E9E9E'
    };
    return {
      backgroundColor: `${colorMap[status.toLowerCase()]}20`,
      color: colorMap[status.toLowerCase()]
    };
  };

  // console.log('Matches type: ', typeof(matches));

  return (
    <>
      <div className="container">
        <h1 className="page-title">All Matches</h1>
        <div className="generate-match-schedule-btn-container">
          <Link to={`/admin/tournaments/${tournamentId}/generate-schedule`}>
            <button className="generate-match-schedule-btn">Generate Match Schedule</button>
          </Link>
        </div>
        

        <div className="matches-grid">
          {matches.length > 0 ? (
            matches.map((match) => (
              <Link
                key={match.id}
                to={`/matches/${match.id}`}
                className="match-card-link"
              >
                <div
                  className={`match-card status-${match.status.toLowerCase()}${animatingMatchId === match.id ? ' animating' : ''}`}
                  data-match-id={match.id}
                >
                  <div className="match-header">
                    <div className="match-id">#{match.id}</div>
                    <div className="match-category">{match.category} - {match.group}</div>
                  </div>
                  
                  <div className="players">
                    <div className="player">
                      <div className="player-name">{match.player1}</div>
                      {/* <small>ID: {match.player1_id}</small> */}
                    </div>

                    <div className="vs">vs</div>

                    <div className="player">
                      <div className="player-name">{match.player2}</div>
                      {/* <small>ID: {match.player2_id}</small> */}
                    </div>
                  </div>

                  <div className="score">
                    {match.score1} : {match.score2}
                  </div>

                  <div className="status">
                    <span
                      className={`status-badge status-${match.status.toLowerCase()}`}
                      style={getStatusColor(match.status)}
                    >
                      {match.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="umpire-section">
                    <span className="umpire-label">
                      Umpire:{' '}
                      <span className="umpire-name">
                        {match.umpire || 'To Be Assigned'}
                      </span>
                    </span>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <div className="no-matches">No matches</div>
          )}
        </div>
      </div>
    </>
  );
};

export default MatchesPage;
