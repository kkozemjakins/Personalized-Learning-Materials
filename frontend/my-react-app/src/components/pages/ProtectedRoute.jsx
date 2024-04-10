import React from 'react';
import { Route, Navigate } from 'react-router-dom';

const ProtectedRoute = ({ element, requiredRole }) => {
  // Assume you have a function to check if the user is logged in and has the required role
  const isLoggedIn = true; // Replace with your logic to check if user is logged in
  const userRole = 'admin'; // Replace with your logic to get user role

  if (!isLoggedIn || userRole !== requiredRole) {
    // If user is not logged in or doesn't have the required role, redirect to login page
    return <Navigate to="/login" />;
  }

  // If user is logged in and has the required role, render the component
  return <Route element={element} />;
};

export default ProtectedRoute;
