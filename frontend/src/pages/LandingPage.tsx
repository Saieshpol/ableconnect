import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles, HeartHandshake, Shield, GraduationCap, Volume2,
  Users, CheckCircle2, ArrowRight, Eye, Layers, Lock, Award
} from 'lucide-react';

interface LandingPageProps {
  onNavigate: (view: 'landing' | 'teacher' | 'student' | 'guardian') => void;
  onOpenLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate, onOpenLogin }) => {
  const { switchRole } = useAuth();

  const handleLaunchPersona = async (role: 'teacher' | 'student' | 'guardian', studentId?: number) => {
    if (import.meta.env.DEV) {
      await switchRole(role, studentId);
      onNavigate(role);
    } else {
      onOpenLogin();
    }
  };

  return (
    <div className="space-y-16 pb-16">
      {/* 1. Hero Section */}
      <section className="relative overflow-hidden pt-12 sm:pt-20 pb-16 border-b border-slate-200 bg-gradient-to-b from-teal-50/70 via-white to-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-100 text-teal-900 text-xs font-bold shadow-xs">
            <Sparkles className="w-4 h-4 text-teal-600" />
            <span>Inclusive Educational Communication Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-tight">
            Better Understanding. Easier Communication.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 via-teal-500 to-cyan-600">
              Inclusive Education.
            </span>
          </h1>

          <p className="text-base sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
            AbleConnect empowers teachers, neurodiverse learners, and students with speech, hearing, visual, or physical impairments through personalized two-way communication.
          </p>

          {/* Persona Launchpad */}
          <div className="pt-4 max-w-3xl mx-auto">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Explore Live Personas Instantly
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                onClick={() => handleLaunchPersona('teacher')}
                className="flex items-center gap-3 p-4 rounded-2xl bg-white border-2 border-teal-500/40 hover:border-teal-500 shadow-sm hover:shadow-md transition-all text-left cursor-pointer group"
              >
                <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                  <GraduationCap className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-extrabold text-sm text-slate-900 group-hover:text-teal-700">
                    Teacher Portal
                  </div>
                  <div className="text-xs text-slate-500">Sarah Jenkins (Lead)</div>
                </div>
              </button>

              <button
                onClick={() => handleLaunchPersona('student', 1)}
                className="flex items-center gap-3 p-4 rounded-2xl bg-white border-2 border-cyan-500/40 hover:border-cyan-500 shadow-sm hover:shadow-md transition-all text-left cursor-pointer group"
              >
                <div className="w-10 h-10 rounded-xl bg-cyan-600 text-white flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-extrabold text-sm text-slate-900 group-hover:text-cyan-700">
                    Student Interface
                  </div>
                  <div className="text-xs text-slate-500">Leo Vance (AAC Mode)</div>
                </div>
              </button>

              <button
                onClick={() => handleLaunchPersona('guardian')}
                className="flex items-center gap-3 p-4 rounded-2xl bg-white border-2 border-amber-500/40 hover:border-amber-500 shadow-sm hover:shadow-md transition-all text-left cursor-pointer group"
              >
                <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                  <Shield className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-extrabold text-sm text-slate-900 group-hover:text-amber-700">
                    Guardian Portal
                  </div>
                  <div className="text-xs text-slate-500">David Chen (Parent)</div>
                </div>
              </button>
            </div>
          </div>

          {/* Compliance Cues */}
          <div className="flex flex-wrap items-center justify-center gap-6 pt-6 text-xs text-slate-500 font-semibold">
            <span className="flex items-center gap-1.5">
              <Award className="w-4 h-4 text-teal-600" />
              <span>WCAG 2.2 AA Compliant</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Lock className="w-4 h-4 text-teal-600" />
              <span>Child Safety & Privacy First</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Volume2 className="w-4 h-4 text-teal-600" />
              <span>Web Speech Synthesis Enabled</span>
            </span>
          </div>
        </div>
      </section>

      {/* 2. Three Pillars Feature Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Designed for Every Stakeholder
          </h2>
          <p className="text-sm text-slate-500 mt-2">
            AbleConnect breaks traditional barriers by tailoring every interface to individual communication requirements.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Pillar 1: Teacher */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs flex flex-col justify-between hover:border-teal-500/50 transition-colors">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center font-bold">
                <GraduationCap className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-xl text-slate-900">For Teachers</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Understand each student's communication preferences and sensory needs. Simplify complex instructions into clear, step-by-step visual guides.
              </p>
              <ul className="space-y-2 text-xs font-semibold text-slate-700">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-600" />
                  <span>"How to Communicate With This Student" guides</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-600" />
                  <span>AI and rule-based Instruction Simplifier</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-600" />
                  <span>Dignified real-time student request queue</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => handleLaunchPersona('teacher')}
              className="mt-6 flex items-center justify-between px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-all cursor-pointer"
            >
              <span>Open Teacher Portal</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Pillar 2: Student */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border-2 border-teal-500/40 shadow-sm flex flex-col justify-between hover:border-teal-500 transition-colors">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-cyan-50 text-cyan-600 flex items-center justify-center font-bold">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-xl text-slate-900">For Students</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Express thoughts, needs, and emotions without relying solely on speech. Large touch-friendly cards, voice synthesis, and one-tap help requests.
              </p>
              <ul className="space-y-2 text-xs font-semibold text-slate-700">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                  <span>Visual AAC Picture Communication Board</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                  <span>Multi-card sentence builder & Web Speech</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                  <span>Gentle, non-stigmatizing help button</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => handleLaunchPersona('student', 1)}
              className="mt-6 flex items-center justify-between px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition-all cursor-pointer"
            >
              <span>Open Student Interface</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Pillar 3: Guardian */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs flex flex-col justify-between hover:border-teal-500/50 transition-colors">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
                <Shield className="w-6 h-6" />
              </div>
              <h3 className="font-extrabold text-xl text-slate-900">For Guardians</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Collaborate directly with educators. Share vital support strategies, review communication preferences, and track individual learning progress.
              </p>
              <ul className="space-y-2 text-xs font-semibold text-slate-700">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-amber-600" />
                  <span>Authorized student profile updates</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-amber-600" />
                  <span>Private educator collaboration channel</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-amber-600" />
                  <span>Consent workflows & transparency</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => handleLaunchPersona('guardian')}
              className="mt-6 flex items-center justify-between px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-all cursor-pointer"
            >
              <span>Open Guardian Portal</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
