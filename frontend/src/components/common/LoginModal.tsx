import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { X, Lock, Mail, GraduationCap, Sparkles, Shield, AlertCircle, ShieldCheck } from 'lucide-react';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { login, switchRole } = useAuth();
  const [email, setEmail] = useState(import.meta.env.DEV ? 'teacher@ableconnect.org' : '');
  const [password, setPassword] = useState(import.meta.env.DEV ? 'teacher123' : '');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login(email, password);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = async (role: 'teacher' | 'student' | 'guardian' | 'admin', studentId?: number) => {
    setError(null);
    setIsLoading(true);
    try {
      await switchRole(role, studentId);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Quick login failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="login-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8 relative border border-slate-100">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-teal-50 text-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-inner">
            <Lock className="w-6 h-6" />
          </div>
          <h2 id="login-title" className="text-2xl font-bold text-slate-900">
            Sign In to AbleConnect
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            {import.meta.env.DEV ? 'Choose a local demo persona or enter account credentials.' : 'Enter your account credentials to continue.'}
          </p>
        </div>

        {import.meta.env.DEV && <><div className="mb-6">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2.5">
            Instant Demo Profiles
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickLogin('teacher')}
              className="flex items-center gap-2 p-2.5 rounded-xl border border-teal-200 bg-teal-50/50 hover:bg-teal-100/60 text-teal-900 text-left transition-all group"
            >
              <div className="w-7 h-7 rounded-lg bg-teal-500 text-white flex items-center justify-center font-bold text-xs shrink-0 group-hover:scale-105 transition-transform">
                <GraduationCap className="w-4 h-4" />
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-bold truncate">Sarah Jenkins</div>
                <div className="text-[10px] text-teal-700 font-medium">Lead Teacher</div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickLogin('student', 1)}
              className="flex items-center gap-2 p-2.5 rounded-xl border border-cyan-200 bg-cyan-50/50 hover:bg-cyan-100/60 text-cyan-900 text-left transition-all group"
            >
              <div className="w-7 h-7 rounded-lg bg-cyan-500 text-white flex items-center justify-center font-bold text-xs shrink-0 group-hover:scale-105 transition-transform">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-bold truncate">Leo Vance</div>
                <div className="text-[10px] text-cyan-700 font-medium">Student (AAC)</div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickLogin('student', 2)}
              className="flex items-center gap-2 p-2.5 rounded-xl border border-purple-200 bg-purple-50/50 hover:bg-purple-100/60 text-purple-900 text-left transition-all group"
            >
              <div className="w-7 h-7 rounded-lg bg-purple-500 text-white flex items-center justify-center font-bold text-xs shrink-0 group-hover:scale-105 transition-transform">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-bold truncate">Maya Patel</div>
                <div className="text-[10px] text-purple-700 font-medium">Student (Step)</div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickLogin('guardian')}
              className="flex items-center gap-2 p-2.5 rounded-xl border border-amber-200 bg-amber-50/50 hover:bg-amber-100/60 text-amber-900 text-left transition-all group"
            >
              <div className="w-7 h-7 rounded-lg bg-amber-500 text-white flex items-center justify-center font-bold text-xs shrink-0 group-hover:scale-105 transition-transform">
                <Shield className="w-4 h-4" />
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-bold truncate">David Chen</div>
                <div className="text-[10px] text-amber-700 font-medium">Guardian</div>
              </div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('admin')}
              className="col-span-2 flex items-center gap-2 rounded-xl border border-violet-200 bg-violet-50/60 p-2.5 text-left text-violet-900 transition-all hover:bg-violet-100/60"
            >
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-violet-600 text-white"><ShieldCheck className="h-4 w-4" /></span>
              <span><span className="block text-xs font-bold">Platform Administrator</span><span className="block text-[10px] font-medium text-violet-700">Admin portal</span></span>
            </button>
          </div>
        </div></>}

        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-slate-400 font-semibold">Or use credentials</span>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none"
                placeholder="teacher@ableconnect.org"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl shadow-sm text-sm transition-all disabled:opacity-50"
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};
