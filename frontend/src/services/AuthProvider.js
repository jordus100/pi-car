import React, { createContext, useState, useEffect } from 'react';
import {Api} from './Api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [username, setUsername] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkSession = async () => {
            try {
                const response = await Api.get('/check_session');
                if (response.status === 200) {
                    setIsAuthenticated(true);
                    setUsername(response.data.username);
                    if (response.data.isAdmin) {
                        setIsAdmin(true);
                    } else {
                        setIsAdmin(false);
                    }
                } else {
                    setIsAuthenticated(false);
                }
            } catch (error) {
                console.error('Failed to check session:', error);
                setIsAuthenticated(false);
            } finally {
                setLoading(false);
            }
        };

        checkSession();
    }, []);

    const login = async (username, password) => {
        try {
            const response = await Api.post('/login',
                { username, password },
            );
            if (response.status === 200) {
                setIsAuthenticated(true);
                setUsername(username);
                if (response.data.isAdmin) {
                    setIsAdmin(true);
                } else {
                    setIsAdmin(false);
                }
                return true;
            } else {
                setIsAuthenticated(false);
                return false;
            }
        } catch (error) {
            console.error('Login failed:', error);
            setIsAuthenticated(false);
            return false;
        }
    };

    const logout = async () => {
        try {
            const response = await Api.post('/logout', {});
            if (response.status === 200) {
                setIsAuthenticated(false);
            } else {
                console.error('Failed to logout');
            }
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, username, isAdmin, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};