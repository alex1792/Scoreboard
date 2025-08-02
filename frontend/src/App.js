import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import BaseLayout from './components/layout/BaseLayout';
import ScoreboardPage from './pages/match/ScoreboardPage';
import MatchesPage from './pages/match/MatchesPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import Home from './pages/HomePage';
import Users from './pages/admin/UsersPage';
import ManageMatch from './pages/admin/ManageMatchPage';
import CreateMatch from './pages/admin/CreateMatchPage';
import AssignUmpirePage from './pages/admin/AssignUmpirePage';
import ChangeUserStaus from './pages/admin/ChangesUserRolePage'; 
import UploadSchedule from './pages/admin/UploadSchedulePage';
import SchedulerPage from './pages/admin/SchedulerPage';
import MatchGenerator from './pages/tournament/MatchGeneratorPage';
import CreateTournament from './pages/admin/CreateTournamentPage';
import TournamentPage from './pages/tournament/TournamentPage';
import SignUpTournamentPage from './pages/tournament/SignUpTournamentPage';
import CheckRegistrationPage from './pages/tournament/CheckRegistrationPage';
import UploadRegistrationPage from './pages/tournament/UploadRegistrationPage';
import GenerateSchedulePage from './pages/admin/GenerateSchedulePage';
import SchedulePage from './pages/tournament/SchedulePage';
import { AuthProvider } from './context/AuthContext';
import { PrivateRoute, AdminRoute, UmpireRoute, HostRoute, HostOrUmpireRoute } from './components/PrivateRoute';

function App() {
  // handle logout
  function LogoutHandler() {
    const navigate = useNavigate();
    useEffect(() => {
      // remove user's token
      localStorage.removeItem('access_token');
      // navigate to homepage
      navigate('/');
    }, [navigate]);
  }

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<BaseLayout />}>
            {/* General Features */}
            <Route path="tournaments/:tournamentId/matches" element={<MatchesPage />} />
            <Route path="matches/:matchId" element={<ScoreboardPage />} />
            <Route path="tournaments" element={<TournamentPage />} />
            <Route path="tournaments/:tournamentId/signup" element={<SignUpTournamentPage />} />
            <Route path="tournaments/:tournamentId/check-registration" element={<CheckRegistrationPage />} />
            <Route path="tournaments/:tournamentId/upload-registration" element={<UploadRegistrationPage />} />
            <Route path="tournaments/:tournamentId/schedule" element={<SchedulePage />} />
            
            {/* Admin Features */}
            <Route path="/admin/set-umpire" element={<AdminRoute><AssignUmpirePage /></AdminRoute>} />
            <Route path="/admin/users" element={<AdminRoute><Users /></AdminRoute>} />
            <Route path="admin/manage-matches" element={<AdminRoute><ManageMatch /></AdminRoute>} />
            <Route path="admin/create-match" element={<HostRoute><CreateMatch /></HostRoute>} />
            <Route path="admin/update-user-role" element={<AdminRoute><ChangeUserStaus /></AdminRoute>} />
            <Route path="/admin/upload-schedule" element={<AdminRoute><UploadSchedule /></AdminRoute>} />
            <Route path="/admin/scheduler" element={<HostRoute><SchedulerPage /></HostRoute>} />
            <Route path="/admin/match-generator" element={<HostRoute><MatchGenerator /></HostRoute>} />
            <Route path="/admin/create-tournament" element={<HostRoute><CreateTournament /></HostRoute>} />
            <Route path="/admin/tournaments/:tournamentId/generate-schedule" element={<AdminRoute><GenerateSchedulePage /></AdminRoute>} />
            
            {/* Home */}
            <Route path="/" element={<Home />} />
            
            {/* Autherization Features */}
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="logout" element={<LogoutHandler />} />
            
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
