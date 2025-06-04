import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import BaseLayout from './BaseLayout';
import ScoreboardPage from './ScoreboardPage';
import MatchesPage from './MatchesPage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import Home from './HomePage'; // 注意這裡是 import Home，不是 HomePage（除非你檔名是 HomePage.jsx，但 export default Home）

// 這裡的 currentUser 可以根據你的登入狀態設定
const currentUser = {
  isAuthenticated: false,
  username: '',
  id: 0,
  role: ''
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<BaseLayout currentUser={currentUser} />}>
          {/* 首頁預設顯示 Home */}
          <Route index element={<Home currentUser={currentUser} />} />
          <Route path="scoreboard" element={<ScoreboardPage />} />
          <Route path="matches" element={<MatchesPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          {/* 如果有管理裁判頁面 */}
          {/* <Route path="admin/set-umpire" element={<AdminSetUmpirePage />} /> */}
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
