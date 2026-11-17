import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useAccessibility } from '../context/AccessibilityContext';
import { AACBoard } from '../components/student/AACBoard';
import { StudentHelpButton } from '../components/student/StudentHelpButton';
import { EmotionCheckinModal } from '../components/student/EmotionCheckinModal';
import { ClassroomScheduleView } from '../components/teacher/ClassroomScheduleView';
import { api } from '../services/api';
import { speech } from '../services/speech';
import { StudentDetail, StudentRequest } from '../types';
import {
  Sparkles, Smile, Volume2, Calendar, LifeBuoy, Heart,
  CheckCircle2, ArrowLeft, BookOpen, Clock, UserCheck
} from 'lucide-react';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const { speakText } = useAccessibility();
  const [studentProfile, setStudentProfile] = useState<StudentDetail | null>(null);
  const [activeTab, setActiveTab] = useState<'aac' | 'schedule' | 'help'>('aac');
  const [isEmotionModalOpen, setIsEmotionModalOpen] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchSelf = async () => {
      try {
        const data = await api.getStudentSelf();
        setStudentProfile(data);
      } catch {
        // Fallback demo profile for Leo Vance
        setStudentProfile({
          id: 1,
          user_id: 2,
          student_code: 'STU-0101',
          full_name: user?.full_name || 'Leo Vance',
          email: 'leo@ableconnect.org',
          avatar_color: 'teal',
          interface_mode: 'visual_aac',
          assistance_level: 'moderate',
          alert_preferences: 'gentle_visual',
          support_instructions: [],
          classes: ['Room 102 - Inclusive Grade 3'],
        });
      }
    };
    fetchSelf();
  }, [user]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleSpeakName = () => {
    if (studentProfile) {
      speech.speak(`Hello ${studentProfile.full_name}. Welcome to your dashboard.`);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6 select-none">
      {/* 1. Student Welcoming Header (Large, Calm, Tactile) */}
      <div className="bg-gradient-to-r from-teal-500 to-cyan-600 rounded-3xl p-5 sm:p-7 text-white shadow-md flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={handleSpeakName}
            className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-white text-teal-800 flex items-center justify-center font-black text-2xl sm:text-3xl shadow-sm hover:scale-105 active:scale-95 transition-transform cursor-pointer"
            title="Tap to hear your name"
          >
            {studentProfile?.full_name?.charAt(0) || 'L'}
          </button>
          <div>
            <div className="text-xs uppercase font-extrabold tracking-widest text-teal-100 mb-0.5">
              My Student Workspace
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
              Hello, {studentProfile?.full_name || 'Leo'}!
            </h1>
            <p className="text-xs sm:text-sm text-teal-100 mt-1 font-medium flex items-center gap-2">
              <span>{studentProfile?.classes[0] || 'Room 102'}</span>
              <span>•</span>
              <button
                onClick={handleSpeakName}
                className="inline-flex items-center gap-1 underline cursor-pointer"
              >
                <Volume2 className="w-4 h-4" />
                <span>Hear Greeting</span>
              </button>
            </p>
          </div>
        </div>

        {/* Emotion Check-in Trigger Pill */}
        <button
          onClick={() => {
            setIsEmotionModalOpen(true);
            speakText("How are you feeling today?");
          }}
          className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white/20 hover:bg-white/30 backdrop-blur-md border border-white/30 text-white font-extrabold text-sm sm:text-base shadow-sm hover:scale-102 active:scale-95 transition-all cursor-pointer"
        >
          <Smile className="w-6 h-6 text-yellow-300" />
          <span>{currentEmotion ? `Feeling: ${currentEmotion}` : 'How do you feel?'}</span>
        </button>
      </div>

      {/* Toast Announcement */}
      {toastMessage && (
        <div className="p-4 bg-emerald-600 text-white rounded-2xl font-bold text-center shadow-lg animate-in fade-in">
          {toastMessage}
        </div>
      )}

      {/* 2. Primary Student Mode Navigation (Huge Touch Targets) */}
      <div className="grid grid-cols-3 gap-3" role="tablist">
        <button
          onClick={() => {
            setActiveTab('aac');
            speakText("Picture communication board");
          }}
          className={`flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3 p-4 sm:p-5 rounded-2xl border-3 transition-all cursor-pointer ${
            activeTab === 'aac'
              ? 'bg-teal-600 text-white border-teal-700 shadow-md scale-102 font-black'
              : 'bg-white text-slate-800 border-slate-200 hover:bg-teal-50 font-bold'
          }`}
        >
          <Sparkles className="w-7 h-7 sm:w-8 sm:h-8" />
          <span className="text-base sm:text-lg">Picture Board</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('help');
            speakText("Ask for help");
          }}
          className={`flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3 p-4 sm:p-5 rounded-2xl border-3 transition-all cursor-pointer ${
            activeTab === 'help'
              ? 'bg-amber-500 text-slate-950 border-amber-600 shadow-md scale-102 font-black'
              : 'bg-white text-slate-800 border-slate-200 hover:bg-amber-50 font-bold'
          }`}
        >
          <LifeBuoy className="w-7 h-7 sm:w-8 sm:h-8" />
          <span className="text-base sm:text-lg">Need Help</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('schedule');
            speakText("My schedule");
          }}
          className={`flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3 p-4 sm:p-5 rounded-2xl border-3 transition-all cursor-pointer ${
            activeTab === 'schedule'
              ? 'bg-indigo-600 text-white border-indigo-700 shadow-md scale-102 font-black'
              : 'bg-white text-slate-800 border-slate-200 hover:bg-indigo-50 font-bold'
          }`}
        >
          <Calendar className="w-7 h-7 sm:w-8 sm:h-8" />
          <span className="text-base sm:text-lg">My Schedule</span>
        </button>
      </div>

      {/* 3. Tab Area Display */}
      {activeTab === 'aac' && (
        <div className="space-y-6">
          <AACBoard
            onSentToTeacher={(sentence: string) => showToast(`Message sent to teacher: "${sentence}"`)}
          />
        </div>
      )}

      {activeTab === 'help' && (
        <div className="space-y-6">
          <StudentHelpButton
            onRequestSent={(req: StudentRequest) => showToast(`Help request "${req.message}" sent to teacher!`)}
          />
        </div>
      )}

      {activeTab === 'schedule' && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
          <ClassroomScheduleView isStudentMode={true} />
        </div>
      )}

      {/* Emotion Modal */}
      <EmotionCheckinModal
        isOpen={isEmotionModalOpen}
        onClose={() => setIsEmotionModalOpen(false)}
        onComplete={(emotion: string) => {
          setCurrentEmotion(emotion);
          showToast(`Checked in as feeling: ${emotion}`);
        }}
      />
    </div>
  );
};
