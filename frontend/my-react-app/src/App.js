import React, { } from 'react';
import './App.css';
  
import {BrowserRouter, Routes, Route, Link} from 'react-router-dom';
  
import LandingPage from "./components/pages/LandningPage.jsx";
import LoginPage from './components/pages/LoginPage.jsx'
import RegisterPage from './components/pages/RegisterPage.jsx'

import UserMainPage from './components/pages/User/UserMainPage.jsx'
import UserTestPage from "./components/pages/User/UserTestPage.jsx";
import UserTestResultPage from "./components/pages/User/UserTestResultsPage.jsx";
import UserCoursePage from "./components/pages/User/UserCoursePage.jsx";

import AdminMainPage from './components/pages/Admin/AdminMainPage.jsx'
import AdminManageUsersPage from './components/pages/Admin/AdminManageUsersPage.jsx'
import AdminManageProfPage from './components/pages/Admin/AdminManageProfPage.jsx'
import AdminManageTestPage from './components/pages/Admin/AdminManageTestPage.jsx'
 
function App() {
  return (
    <div className="vh-100 gradient-custom">
    <div className="container">
      <h1 className="page-header text-center">React and Python Flask EDU system</h1>
   
      <BrowserRouter>
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/logout" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route path="/user_main" element={<UserMainPage />} />
            <Route path="/profession_test/:id" element={<UserTestPage />} />
            <Route path="/user_test_results" element={<UserTestResultPage />} />
            <Route path="/user_courses" element={<UserCoursePage />} />

            <Route path="/admin_main" element={<AdminMainPage />} />
            <Route path="/admin_users" element={<AdminManageUsersPage />} />
            <Route path="/admin_prof" element={<AdminManageProfPage />} />
            <Route path="/admin_test" element={<AdminManageTestPage />} />
            


        </Routes>
      </BrowserRouter>
    </div>
    </div>
  );
}
   
export default App;