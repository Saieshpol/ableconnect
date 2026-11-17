import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AccessibilityProvider } from './context/AccessibilityContext';
import { AccessibilityBar } from './components/common/AccessibilityBar';
import { Navbar } from './components/common/Navbar';
import { LoginModal } from './components/common/LoginModal';
import { LandingPage } from './pages/LandingPage';
import { TeacherDashboard } from './pages/TeacherDashboard';
import { StudentDashboard } from './pages/StudentDashboard';
import { GuardianPortal } from './pages/GuardianPortal';
import { AdminDashboard } from './pages/AdminDashboard';

const AppContent: React.FC = () => {
  const { role, isAuthenticated } = useAuth();
  const [currentView, setCurrentView] = useState<'landing' | 'teacher' | 'student' | 'guardian' | 'admin'>('landing');
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  // Auto-route based on authenticated role if not explicitly set to landing
  useEffect(() => {
    if (isAuthenticated && role) {
      if (role === 'teacher') setCurrentView('teacher');
      else if (role === 'student') setCurrentView('student');
      else if (role === 'guardian') setCurrentView('guardian');
      else if (role === 'admin') setCurrentView('admin');
    }
  }, [role, isAuthenticated]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-teal-200 selection:text-teal-900">
      {/* 1. Global Accessibility & Demo Bar */}
      <AccessibilityBar />

      {/* 2. Global Navigation */}
      <Navbar
        currentView={currentView}
        onNavigate={(view) => setCurrentView(view)}
        onOpenLogin={() => setIsLoginOpen(true)}
      />

      {/* 3. Main Workspace */}
      <main className="grow">
        {currentView === 'landing' && (
          <LandingPage
            onNavigate={(view) => setCurrentView(view)}
            onOpenLogin={() => setIsLoginOpen(true)}
          />
        )}

        {currentView === 'teacher' && <TeacherDashboard />}
        {currentView === 'student' && <StudentDashboard />}
        {currentView === 'guardian' && <GuardianPortal />}
        {currentView === 'admin' && <AdminDashboard />}
      </main>

      {/* 4. Accessible Semantic Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800">AbleConnect</span>
            <span>•</span>
            <span>WCAG 2.2 AA Inclusive Education Platform</span>
          </div>
          <div className="text-slate-400">
            Dedicated to respectful, personalized student-teacher communication.
          </div>
        </div>
      </footer>

      {/* Login Dialog */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onSuccess={() => {
          // View will auto-adjust via useEffect on role change
        }}
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AccessibilityProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </AccessibilityProvider>
  );
};

export default App;
