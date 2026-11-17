import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sparkles, HeartHandshake, LogOut, LogIn, GraduationCap, User as UserIcon, Shield } from 'lucide-react';

interface NavbarProps {
  currentView: 'landing' | 'teacher' | 'student' | 'guardian';
  onNavigate: (view: 'landing' | 'teacher' | 'student' | 'guardian') => void;
  onOpenLogin: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, onNavigate, onOpenLogin }) => {
  const { user, isAuthenticated, logout, role } = useAuth();

  return (
    <header className="bg-white/95 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <button
          onClick={() => onNavigate('landing')}
          className="flex items-center gap-3 text-left focus:outline-none focus:ring-2 focus:ring-teal-500 rounded-lg p-1 group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-600 via-teal-500 to-cyan-400 flex items-center justify-center text-white shadow-md shadow-teal-500/20 group-hover:scale-105 transition-transform">
            <HeartHandshake className="w-6 h-6" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-xl tracking-tight text-slate-900">
                Able<span className="text-teal-600">Connect</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-teal-100 text-teal-800">
                Inclusive
              </span>
            </div>
            <p className="text-[11px] text-slate-500 hidden sm:block">
              Better Understanding. Easier Communication.
            </p>
          </div>
        </button>

        {/* Center Nav Views */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-100/80 p-1 rounded-xl border border-slate-200/60" aria-label="Portal Navigation">
          <button
            onClick={() => onNavigate('landing')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentView === 'landing'
                ? 'bg-white text-slate-900 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => onNavigate('teacher')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentView === 'teacher'
                ? 'bg-white text-teal-700 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-teal-700'
            }`}
          >
            <GraduationCap className="w-4 h-4 text-teal-600" />
            <span>Teacher Portal</span>
          </button>
          <button
            onClick={() => onNavigate('student')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentView === 'student'
                ? 'bg-white text-cyan-700 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-cyan-700'
            }`}
          >
            <Sparkles className="w-4 h-4 text-cyan-600" />
            <span>Student Interface</span>
          </button>
          <button
            onClick={() => onNavigate('guardian')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentView === 'guardian'
                ? 'bg-white text-amber-700 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-amber-700'
            }`}
          >
            <Shield className="w-4 h-4 text-amber-600" />
            <span>Guardian Portal</span>
          </button>
        </nav>

        {/* User Auth Info & Actions */}
        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 pl-2">
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.full_name}
                    className="w-8 h-8 rounded-full object-cover ring-2 ring-teal-500/30"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center font-bold text-xs">
                    {user.full_name.charAt(0)}
                  </div>
                )}
                <div className="hidden sm:block text-left">
                  <div className="text-xs font-bold text-slate-800 leading-tight">
                    {user.full_name}
                  </div>
                  <div className="text-[10px] uppercase font-semibold text-teal-600 capitalize">
                    {user.role}
                  </div>
                </div>
              </div>
              <button
                onClick={logout}
                className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                title="Log Out"
                aria-label="Log Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenLogin}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-sm shadow-sm transition-all hover:shadow"
            >
              <LogIn className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
