import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = async (username, password) => {
    try {
      const response = await fetch('/api/generate_token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.token);
        setIsAuthenticated(true);
        return true;
      } else {
        alert(data.message);
        return false;
      }
    } catch (error) {
      console.error(error);
      alert('Error logging in');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  const checkAuth = () => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};