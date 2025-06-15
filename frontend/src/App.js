import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import BaseLayout from './BaseLayout';
import ScoreboardPage from './ScoreboardPage';
import MatchesPage from './MatchesPage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import Home from './HomePage';
import Users from './UsersPage';
import ManageMatch from './ManageMatchPage';
import CreateMatch from './CreateMatchPage';
import AssignUmpirePage from './AssignUmpirePage';
import ChangeUserStaus from './ChangesUserRolePage'; 
import UploadSchedule from './UploadSchedulePage';
import { AuthProvider } from './AuthContext';

// currentUser can be modified to reflect the actual user state
const currentUser = {
  isAuthenticated: false,
  username: '',
  id: 0,
  role: ''
};

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
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<BaseLayout currentUser={currentUser} />}>
            {/* General Features */}
            <Route path="matches" element={<MatchesPage />} />
            <Route path="matches/:matchId" element={<ScoreboardPage currentUser={currentUser}/>} />
            
            {/* Admin Features */}
            <Route path="/admin/set-umpire" element={<AssignUmpirePage />} />
            <Route path="/admin/users" element={<Users />} />
            <Route path="admin/manage-matches" element={<ManageMatch />} />
            <Route path="admin/create-match" element={<CreateMatch />} />
            <Route path="admin/update-user-role" element={<ChangeUserStaus />} />
            <Route path="/admin/upload-schedule" element={<UploadSchedule />} />
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
