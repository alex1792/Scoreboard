import React, { useState, useEffect } from 'react';
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
import { AuthProvider } from './context/AuthContext';

// currentUser can be modified to reflect the actual user state
// const currentUser = {
//   isAuthenticated: false,
//   username: '',
//   id: 0,
//   role: ''
// };

function App() {
  const [currentUser, setCurrentUser] = useState(null);

  // handle logout
  function LogoutHandler() {
    const navigate = useNavigate();
    useEffect(() => {
      // remove user's token
      localStorage.removeItem('access_token');
      // set currentUser to null
      setCurrentUser(null);
      // navigate to homepage
      navigate('/');
    }, [navigate]);
  }

  // useEffect(() => {
  //   console.log('currentUser.role in App: ',currentUser?.role);
  // }, [currentUser]);
  

  return (
    <AuthProvider currentUser={currentUser} setCurrentUser={setCurrentUser}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<BaseLayout currentUser={currentUser} />}>
            {/* General Features */}
            <Route path="tournaments/:tournamentId/matches" element={<MatchesPage />} />
            <Route path="matches/:matchId" element={<ScoreboardPage currentUser={currentUser}/>} />
            <Route path="tournaments" element={<TournamentPage />} />
            <Route path="tournaments/:tournamentId/signup" element={<SignUpTournamentPage />} />
            <Route path="tournaments/:tournamentId/check-registration" element={<CheckRegistrationPage />} />
            
            {/* Admin Features */}
            <Route path="/admin/set-umpire" element={<AssignUmpirePage />} />
            <Route path="/admin/users" element={<Users />} />
            <Route path="admin/manage-matches" element={<ManageMatch />} />
            <Route path="admin/create-match" element={<CreateMatch />} />
            <Route path="admin/update-user-role" element={<ChangeUserStaus />} />
            <Route path="/admin/upload-schedule" element={<UploadSchedule />} />
            <Route path="/admin/scheduler" element={<SchedulerPage />} />
            <Route path="/admin/match-generator" element={<MatchGenerator />} />
            <Route path="/admin/create-tournament" element={<CreateTournament />} />
            {/* <Route path="admin/change-upire-status" element={<AssignUmpirePage />} /> */}

            {/* Home */}
            <Route path="/" element={<Home currentUser={currentUser} />} />
            
            {/* Autherization Features */}
            <Route path="login" element={<LoginPage setCurrentUser={setCurrentUser} />} />
            <Route path="register" element={<RegisterPage setCurrentUser={setCurrentUser}/>} />
            <Route path="logout" element={<LogoutHandler />} />
            
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
