import React from 'react';
import { Link } from 'react-router-dom';
import './TournamentCard.css';

const TournamentCard = ({ 
  tournament, 
  onDelete, 
  showDeleteButton = false,
  showAdminActions = false,
  className = '',
  isClickable = false,
  formatDate,
  hasAdminAccess
}) => {
  // 格式化日期的函數
  const formatDateLocal = (dateString) => {
    if (!dateString) return 'TBD';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      return 'Invalid Date';
    }
  };

  // 使用傳入的 formatDate 函數，如果沒有則使用本地函數
  const formatDateFunction = formatDate || formatDateLocal;

  // 添加格式化 description 的函數
  const formatDescription = (description) => {
    if (!description) return '';
    return description.split('\n').map((line, index) => (
      <span key={index}>
        {line}
        {index < description.split('\n').length - 1 && <br />}
      </span>
    ));
  };

  const cardContent = (
    <div className={`tournament-card-wrapper ${className}`}>
      <div className="tournament-card">
        {showDeleteButton && (
          <button
            className="close-btn"
            aria-label="Close"
            onClick={(e) => { 
              e.preventDefault(); 
              e.stopPropagation(); 
              onDelete(tournament.id); 
            }}
            type="button"
          >
            &times;
          </button>
        )}
        
        <div className="tournament-header">
          <div className="tournament-id">#{tournament.id}</div>
        </div>
        
        <div className="tournament-name">
          {tournament.name}
        </div>

        <div className="tournament-info">
          <div className="info-item">
            <span className="info-label">Start Date:</span>
            <span className="info-value">{formatDateFunction(tournament.start_date)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">End Date:</span>
            <span className="info-value">{formatDateFunction(tournament.end_date)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Status:</span>
            <span className="info-value">{tournament.status || 'TBD'}</span>
          </div>
          
          <div className="info-item">
            <span className="info-label">Location:</span>
            <span className="info-value">{tournament.location || 'TBD'}</span>
          </div>
          
          {tournament.registration_deadline && (
            <div className="info-item">
              <span className="info-label">Registration Deadline:</span>
              <span className="info-value">{formatDateFunction(tournament.registration_deadline)}</span>
            </div>
          )}

          {/* {tournament.description && (
            <div className="info-item description-item">
              <span className="info-label">Description:</span>
              <span className="info-value description-value">
                {formatDescription(tournament.description)}
              </span>
            </div>
          )} */}
        </div>

        <div className="tournament-actions">
          {/* <Link 
            to={`/tournaments/${tournament.id}`}
            className="view-details-btn"
          >
            ℹ View Details
          </Link> */}
          <Link 
            to={`/tournaments/${tournament.id}/signup`}
            className="signup-btn"
          >
            ✍🏻 Sign Up
          </Link>
          <Link 
            to={`/tournaments/${tournament.id}/schedule`}
            className="view-schedule-btn"
          >
            🗓️ View Schedule
          </Link>
          <Link 
            to={`/tournaments/${tournament.id}/matches`}
            className="view-matches-btn"
          >
            🔍 View Matches
          </Link>
          {/* 只有管理員才能看到查看報名信息的按鈕 */}
          {showAdminActions && hasAdminAccess && hasAdminAccess() && (
            <Link 
              to={`/tournaments/${tournament.id}/check-registration`}
              className="view-registrations-btn"
            >
               View Registrations
            </Link>
          )}
        </div>
      </div>
    </div>
  );

  // 如果可點擊，包裝在 Link 中
  if (isClickable) {
    return (
      <Link to={`/tournaments/${tournament.id}`} className="tournament-card-link">
        {cardContent}
      </Link>
    );
  }

  return cardContent;
};

export default TournamentCard;