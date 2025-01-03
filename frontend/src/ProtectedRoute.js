import React, { useContext } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from './services/AuthProvider';

const ProtectedRoute = () => {
  const { isAuthenticated } = useContext(AuthContext);

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;