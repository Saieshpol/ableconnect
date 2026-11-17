import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  activeStudentId: number | null;
  setActiveStudentId: (id: number | null) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  switchRole: (role: UserRole, studentId?: number) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeStudentId, setActiveStudentId] = useState<number | null>(null);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('ableconnect_token');
      if (token) {
        try {
          const profile = await api.getMe();
          setUser(profile);
          if (profile.role === 'student') {
            setActiveStudentId(1); // default demo student Leo Vance
          }
        } catch {
          localStorage.removeItem('ableconnect_token');
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const authData = await api.login(email, password);
      setUser(authData.user);
      if (authData.user.role === 'student') {
        setActiveStudentId(1);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('ableconnect_token');
    setUser(null);
    setActiveStudentId(null);
  };

  const switchRole = async (targetRole: UserRole, studentId?: number) => {
    if (!import.meta.env.DEV) throw new Error('Persona switching is available only in local development.');
    const credentials: Record<UserRole, { email: string; password: string }> = {
      teacher: { email: 'teacher@ableconnect.org', password: 'teacher123' },
      student: { email: studentId === 2 ? 'maya@ableconnect.org' : 'leo@ableconnect.org', password: 'student123' },
      guardian: { email: 'guardian@ableconnect.org', password: 'guardian123' },
      admin: { email: 'admin@ableconnect.org', password: 'admin123' },
    };
    await login(credentials[targetRole].email, credentials[targetRole].password);
    setActiveStudentId(targetRole === 'student' ? (studentId || 1) : null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role: user ? user.role : null,
        isAuthenticated: !!user,
        isLoading,
        activeStudentId,
        setActiveStudentId,
        login,
        logout,
        switchRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
