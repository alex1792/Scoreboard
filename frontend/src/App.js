import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import BaseLayout from './BaseLayout';
import ScoreboardPage from './ScoreboardPage';
import MatchesPage from './MatchesPage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import Home from './HomePage'; // 注意這裡是 import Home，不是 HomePage（除非你檔名是 HomePage.jsx，但 export default Home）
import Users from './UsersPage';
import ManageMatch from './ManageMatchPage';
import CreateMatch from './CreateMatchPage';
import AssignUmpirePage from './AssignUmpirePage';
import { AuthProvider } from './AuthContext';

// 這裡的 currentUser 可以根據你的登入狀態設定
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

  useEffect(() => {
    console.log('currentUser.role in App: ',currentUser?.role);
  }, [currentUser]);
  

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<BaseLayout currentUser={currentUser} />}>
            <Route path="/" element={<Home currentUser={currentUser} />} />
            <Route path="matches" element={<MatchesPage />} />
            <Route path="matches/:matchId" element={<ScoreboardPage currentUser={currentUser}/>} />
            <Route path="login" element={<LoginPage setCurrentUser={setCurrentUser} />} />
            <Route path="register" element={<RegisterPage setCurrentUser={setCurrentUser}/>} />
            <Route path="logout" element={<LogoutHandler />} />
            <Route path="/admin/users" element={<Users />} />

            {/* missing */}
            <Route path="/admin/set-umpire" element={<AssignUmpirePage />} />
            <Route path="admin/manage-matches" element={<ManageMatch />} />
            <Route path="admin/create-match" element={<CreateMatch />} />
            {/* <Route path="admin/assign-umpire" element={<AssignUmpirePage />} /> */}
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
