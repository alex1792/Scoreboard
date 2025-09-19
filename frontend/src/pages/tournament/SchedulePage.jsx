import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTournamentSchedule } from '../../api/api';
import '../../styles/pages/tournament/SchedulePage.css';

const SchedulePage = () => {
  const { tournamentId } = useParams();
  const [scheduleData, setScheduleData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSchedule();
  }, [tournamentId]);

  const loadSchedule = async () => {
    try {
        setLoading(true);
        // console.log('Loading schedule for tournament:', tournamentId);
        
        const response = await getTournamentSchedule(tournamentId);
        // console.log('Schedule response:', response);
        
        // 修正：檢查 response.schedule 和 response.schedule.schedule_by_date
        if (response && response.status === 'success' && response.schedule && response.schedule.schedule_by_date) {
            setScheduleData(response.schedule);
            // console.log('Schedule data set successfully:', response.schedule);
        } else {
            // console.log('Response structure:', response);
            // console.log('No schedule data found in response');
            setError('No schedule data available');
        }
    } catch (err) {
        console.error('Error loading schedule:', err);
        setError(err.message);
    } finally {
        setLoading(false);
    }
};

  const renderMatchInfo = (matchInfo, index) => (
    <div key={index} className="match-item">
      <div className="match-header">
        <span className="court">Court {matchInfo.court}</span>
        <span className="time">{matchInfo.time}</span>
        {matchInfo.round && matchInfo.match_number && (
            <span className="match-id">R{matchInfo.round}-M{matchInfo.match_number}</span>
        )}
      </div>
      <div className="match-content">
        <div className="category">{matchInfo.category}</div>
        <div className="players">
          <span className="player1">{matchInfo.player1}</span>
          <span className="vs">vs</span>
          <span className="player2">{matchInfo.player2}</span>
        </div>
        <div className="status">{matchInfo.status}</div>
      </div>
    </div>
  );

  const renderBatch = (batchNumber, matches) => (
    <div key={batchNumber} className="batch">
      <h3>Batch {batchNumber}</h3>
      <div className="matches">
        {matches.map((match, index) => renderMatchInfo(match, index))}
      </div>
    </div>
  );

  const renderDate = (date, batches) => (
    <div key={date} className="date-section">
      <div className="date-header">
        <h2>{date}</h2>
        <Link 
          to={`/admin/${tournamentId}/upload-schedule`}
          className="upload-schedule-btn"
        >
          Upload Custom Schedule
        </Link>
      </div>
      {Object.entries(batches).map(([batchNumber, matches]) => 
        renderBatch(batchNumber, matches)
      )}
    </div>
  );

  if (loading) {
    return <div className="loading">Loading schedule...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!scheduleData || !scheduleData.schedule_by_date) {
    return <div className="no-schedule">No schedule available</div>;
  }

  return (
    <div className="schedule-page">
      <div className="schedule-header">
        <h1>Tournament Schedule</h1>
        <div className="schedule-info">
          <span>Total Matches: {scheduleData.total_matches || 'N/A'}</span>
        </div>
      </div>
      
      <div className="schedule-content">
        {Object.entries(scheduleData.schedule_by_date).map(([date, batches]) => 
          renderDate(date, batches)
        )}
      </div>
    </div>
  );
};

export default SchedulePage;