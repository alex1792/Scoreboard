import { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { fetchInfoFromBackend, deleteTournament } from '../../api/api';
import TournamentCard from '../../components/tournament/TournamentCard';
import '../../styles/pages/tournament/TournamentPage.css';
import { API_URLS } from '../../config/urls';

const TournamentPage = () => {
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { currentUser } = useContext(AuthContext);

  // Fetch tournaments from backend
  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        console.log('=== Starting to fetch tournaments ===');
        
        console.log('API_URLS.ALL_TOURNAMENTS:', API_URLS.ALL_TOURNAMENTS);
        const data = await fetchInfoFromBackend(API_URLS.ALL_TOURNAMENTS);
        
        console.log('=== Response received ===');
        console.log('Full response:', data);
        
        if (data?.status === 'success') {
          console.log('Fetched tournaments:', data.data);
          setTournaments(data.data);
        } else {
          console.error('API returned error:', data?.message || 'Unknown error');
          setError(data?.message || 'Unknown error');
        }
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err.message || 'Network error');
      } finally {
        console.log('Fetch completed, setting loading to false');
        setLoading(false);
      }
    };

    fetchTournaments();
  }, []);

  const formatDate = (dateString) => {
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

  // 檢查用戶是否有刪除權限
  const hasDeletePermission = (tournament) => {
    if (!currentUser) return false;
    
    // Admin 可以刪除任何 tournament
    if (currentUser.role === 'admin') return true;
    
    // Host 只能刪除自己創建的 tournament
    if (currentUser.role === 'host' && tournament.host_id === currentUser.id) return true;
    
    return false;
  };

  // 檢查用戶是否有查看報名信息的權限（與刪除權限邏輯相同）
  const hasViewRegistrationsPermission = (tournament) => {
    if (!currentUser) return false;
    
    // Admin 可以查看任何 tournament 的報名信息
    if (currentUser.role === 'admin') return true;
    
    // Host 只能查看自己創建的 tournament 的報名信息
    if (currentUser.role === 'host' && tournament.host_id === currentUser.id) return true;
    
    return false;
  };

  // 檢查用戶是否有一般管理權限（用於其他管理功能）
  const hasGeneralAdminAccess = () => {
    return currentUser && (currentUser.role === 'admin' || currentUser.role === 'host' || currentUser.role === 'organizer');
  };

  // 處理刪除 tournament
  const handleDeleteTournament = async (tournamentId) => {
    try {
      console.log('Deleting tournament:', tournamentId);
      
      // 顯示確認對話框
      const confirmed = window.confirm('Are you sure you want to delete this tournament? This action cannot be undone.');
      if (!confirmed) {
        return;
      }

      const response = await deleteTournament(tournamentId);
      
      if (response?.status === 'success') {
        console.log('Tournament deleted successfully');
        // 從本地狀態中移除被刪除的 tournament
        setTournaments(prevTournaments => 
          prevTournaments.filter(tournament => tournament.id !== tournamentId)
        );
      } else {
        console.error('Failed to delete tournament:', response?.message);
        alert('Failed to delete tournament: ' + (response?.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error deleting tournament:', error);
      alert('Error deleting tournament: ' + error.message);
    }
  };

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

  if (error) {
    return (
      <div className="container">
        <h1 className="page-title">All Tournaments</h1>
        <div className="error-message">
          Error: {error}
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container">
        <h1 className="page-title">All Tournaments</h1>
        <div className="loading">Loading tournaments...</div>
      </div>
    );
  }

  // 通用的權限檢查函數
  const hasTournamentPermission = (tournament, action) => {
    if (!currentUser) return false;
    
    // Admin 可以做任何操作
    if (currentUser.role === 'admin') return true;
    
    // Host 只能對自己創建的 tournament 進行操作
    if (currentUser.role === 'host' && tournament.host_id === currentUser.id) return true;
    
    return false;
  };

  return (
    <div className="tournament-page">
      <div className="container">
        <h1 className="page-title">Tournaments</h1>
        
        {loading && <div className="loading">Loading tournaments...</div>}
        
        {error && <div className="error-message">{error}</div>}
        
        {!loading && !error && (
          <>
            {tournaments.length === 0 ? (
              <div className="no-tournaments">
                <p>No tournaments available.</p>
              </div>
            ) : (
              <div className="tournaments-grid">
                {tournaments.map((tournament) => (
                  <TournamentCard
                    key={tournament.id}
                    tournament={tournament}
                    onDelete={handleDeleteTournament}
                    showDeleteButton={hasTournamentPermission(tournament, 'delete')}
                    showAdminActions={true}
                    formatDate={formatDate}
                    hasAdminAccess={() => hasTournamentPermission(tournament, 'view_registrations')}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TournamentPage;
