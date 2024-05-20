import React from 'react';
import './App.css';
import { Breadcrumb, Layout, Menu } from 'antd';
import { BookOutlined } from '@ant-design/icons';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

import LandingPage from './components/pages/LandningPage.jsx';
import LoginPage from './components/pages/LoginPage.jsx';
import RegisterPage from './components/pages/RegisterPage.jsx';

import CoursePage from './components/pages/CoursePages/CoursePage.jsx';
import TheoryPage from './components/pages/CoursePages/TheoryPage.jsx';
import TaskPage from './components/pages/CoursePages/TaskPage.jsx';


import UserMainPage from './components/pages/User/UserMainPage.jsx';
import UserTestPage from './components/pages/User/UserTestPage.jsx';
import UserTestResultPage from './components/pages/User/UserTestResultsPage.jsx';
import UserCoursePage from './components/pages/User/UserCoursePage.jsx';
import UserTaskPage from './components/pages/User/UserTaskPage.jsx';

import AdminMainPage from './components/pages/Admin/AdminMainPage.jsx';
import AdminManageUsersPage from './components/pages/Admin/AdminManageUsersPage.jsx';
import AdminManageProfPage from './components/pages/Admin/AdminManageProfPage.jsx';
import AdminManageTestPage from './components/pages/Admin/AdminManageTestPage.jsx';

const { Header, Content, Footer } = Layout;

function Navbar() {
  return (
    <Menu theme="dark" mode="horizontal" defaultSelectedKeys={['1']} style={{ marginLeft: 'auto' }}>
      <Menu.Item key="1"><Link to="/">Home</Link></Menu.Item>
      <Menu.Item key="2"><Link to="/user_main">Home User</Link></Menu.Item>
      <Menu.Item key="3"><Link to="/login">Login</Link></Menu.Item>
      <Menu.Item key="4"><Link to="/register">Register</Link></Menu.Item>
    </Menu>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <Header
          style={{
            position: 'fixed',
            zIndex: 1,
            width: '100%',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <div style={{ color: 'white' }} className="demo-logo">
            <BookOutlined />Edy AI system
          </div>
          <Navbar />
        </Header>
        <Content style={{ padding: '0 48px', marginTop: 64 }}>
          <Breadcrumb style={{ margin: '16px 0' }}>
            <Breadcrumb.Item>Home</Breadcrumb.Item>
          </Breadcrumb>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/logout" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route path="/course/:id" element={<CoursePage />} />
            <Route path="/task/:id" element={<TaskPage />} />
            <Route path="/theory/:id" element={<TheoryPage />} />

            <Route path="/user_main" element={<UserMainPage />} />
            <Route path="/profession_test/:id" element={<UserTestPage />} />
            <Route path="/user_test_results" element={<UserTestResultPage />} />
            <Route path="/user_courses" element={<UserCoursePage />} />
            <Route path="/user_tasks" element={<UserTaskPage />} />

            <Route path="/admin_main" element={<AdminMainPage />} />
            <Route path="/admin_users" element={<AdminManageUsersPage />} />
            <Route path="/admin_prof" element={<AdminManageProfPage />} />
            <Route path="/admin_test" element={<AdminManageTestPage />} />
          </Routes>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          EdySystem ©{new Date().getFullYear()} Created by KirilsK
        </Footer>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
