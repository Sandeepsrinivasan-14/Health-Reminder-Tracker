import React, { createContext, useContext, useMemo, useState } from "react";
import { setAuthToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);

  const login = (newToken, userData = null) => {
    setToken(newToken);
    setUser(userData);
    setAuthToken(newToken);
  };

  const logout = () => {
    setToken("");
    setUser(null);
    setAuthToken(null);
  };

  const value = useMemo(() => ({
    token,
    user,
    isAuthenticated: !!token,
    login,
    logout,
  }), [token, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
