import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('budgetbuddy_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('budgetbuddy_token'));
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 10000);
      return () => clearInterval(interval);
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
      localStorage.setItem('budgetbuddy_user', JSON.stringify(res.data));
    } catch (err) {
      console.error('Failed to fetch user', err);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      setNotifications(res.data);
    } catch (err) {
      console.error('Failed to fetch notifications', err);
    }
  };

  const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const res = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    const { access_token, user: userData } = res.data;
    localStorage.setItem('budgetbuddy_token', access_token);
    localStorage.setItem('budgetbuddy_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    fetchNotifications();
    return userData;
  };

  const register = async (email, fullName, password, role = 'student') => {
    const res = await api.post('/auth/register', {
      email,
      full_name: fullName,
      password,
      role
    });
    return res.data;
  };

  const verifyEmail = async (email, code) => {
    const res = await api.post('/auth/verify-email', { email, code });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('budgetbuddy_token', access_token);
    localStorage.setItem('budgetbuddy_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    fetchNotifications();
    return userData;
  };

  const resendVerification = async (email) => {
    const res = await api.post('/auth/resend-verification', { email });
    return res.data;
  };

  const oauthLogin = async (provider, email, fullName, providerId) => {
    const res = await api.post('/auth/oauth/login', {
      provider,
      email,
      full_name: fullName,
      provider_id: providerId
    });

    const { access_token, user: userData } = res.data;
    localStorage.setItem('budgetbuddy_token', access_token);
    localStorage.setItem('budgetbuddy_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    fetchNotifications();
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('budgetbuddy_token');
    localStorage.removeItem('budgetbuddy_user');
    setToken(null);
    setUser(null);
    setNotifications([]);
  };

  const markNotificationRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) {
      console.error(err);
    }
  };

  const clearAllNotifications = async () => {
    try {
      await api.delete('/notifications/clear-all');
      setNotifications([]);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      register,
      verifyEmail,
      resendVerification,
      oauthLogin,
      logout,
      notifications,
      fetchNotifications,
      markNotificationRead,
      clearAllNotifications,
      setUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
