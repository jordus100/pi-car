import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './services/AuthProvider';
import './Login.css';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { isAuthenticated, login } = useContext(AuthContext);
  const navigate = useNavigate();

  if (isAuthenticated) {
    navigate('/');
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Clear any previous error message

    const success = await login(username, password);
    if (success) {
      navigate('/');
    } else {
      setError('Invalid username or password. Please try again.');
    }
  };


  return (
    <div className={'Login'}>
      <form onSubmit={handleSubmit}>
        <h1 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Login to surveillance robot</h1>

        {error && <p className={'error'}>{error}</p>}

        <div>
          <label htmlFor="username">Username:</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="password">Password:</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginPage;