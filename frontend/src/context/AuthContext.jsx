/* ==========================================
   SNEAKERSTUFF AUTH REFACTOR
   Modified by Sneakerstuff Developer

   Login now authenticates using email.
   Signup collects username + email.
========================================== */

/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useCallback } from "react";

export const AuthContext = createContext(null);

// Safe Client-Side JWT Decoder
const decodeToken = (token) => {
  if (!token) return null;
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Token decoding failed", error);
    return null;
  }
};

export default function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token") || null);
  
  const [user, setUser] = useState(() => {
    const savedToken = localStorage.getItem("token");
    if (!savedToken) return null;
    const decoded = decodeToken(savedToken);
    if (!decoded) return null;
    
    const storedUser = localStorage.getItem("user");
    let parsedUser = null;
    if (storedUser) {
      try {
        parsedUser = JSON.parse(storedUser);
      } catch (e) {
        console.error("Failed to parse stored user", e);
      }
    }
    
    // Extracted email, username, and signed role from decoded JWT claims
    return {
      id: decoded.sub ? parseInt(decoded.sub, 10) : null,
      username: decoded.username || "",
      email: decoded.email || parsedUser?.email || "",
      role: decoded.role || parsedUser?.role || "user",
    };
  });

  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    const savedToken = localStorage.getItem("token");
    if (!savedToken) return false;
    return !!decodeToken(savedToken);
  });

  const [isLoading] = useState(false);

  const login = useCallback((accessToken, userData = null) => {
    localStorage.setItem("token", accessToken);
    
    let userProfile = null;
    if (userData) {
      localStorage.setItem("user", JSON.stringify(userData));
      userProfile = userData;
    } else {
      const decoded = decodeToken(accessToken);
      
      // Decoded email and role claims are now extracted from JWT and saved in local userProfile state
      userProfile = {
        id: decoded?.sub ? parseInt(decoded.sub, 10) : null,
        username: decoded?.username || "",
        email: decoded?.email || "",
        role: decoded?.role || "user"
      };
      localStorage.setItem("user", JSON.stringify(userProfile));
    }

    setToken(accessToken);
    setUser(userProfile);
    setIsLoggedIn(true);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
    setIsLoggedIn(false);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isLoggedIn,
        isLoading,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}