// Navbar.js
import React from 'react';
import { Menu } from 'antd';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();

  return (
    <Menu theme="dark" mode="horizontal" defaultSelectedKeys={['1']} style={{ marginLeft: 'auto' }}>
      <Menu.Item key="1" onClick={() => navigate('/')}>Home</Menu.Item>
      <Menu.Item key="2" onClick={() => navigate('/login')}>Login</Menu.Item>
      <Menu.Item key="3" onClick={() => navigate('/register')}>Register</Menu.Item>
    </Menu>
  );
};

export default Navbar;
