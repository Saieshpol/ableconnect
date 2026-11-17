import React from 'react';
import { useAccessibility } from '../../context/AccessibilityContext';
import { useAuth } from '../../context/AuthContext';
import { Contrast, Volume2, VolumeX, Eye, UserCheck, FastForward } from 'lucide-react';

export const AccessibilityBar: React.FC = () => {
  const {
    highContrast,
    toggleHighContrast,
    increaseFontScale,
    decreaseFontScale,
    fontScale,
    reducedMotion,
    toggleReducedMotion,
    speechEnabled,
    toggleSpeech,
    speakText,
  } = useAccessibility();

  const { user, role, switchRole } = useAuth();

  return (
    <div
      role="region"
      aria-label="Accessibility and Demo Controls"
      className="bg-slate-900 text-slate-100 px-4 py-2 text-xs md:text-sm flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 shadow-sm transition-all"
    >
      {/* Left: Accessibility Controls */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-semibold text-teal-400 flex items-center gap-1.5 mr-1">
          <Eye className="w-4 h-4 text-teal-300" aria-hidden="true" />
          <span>Accessibility:</span>
        </span>

        {/* High Contrast Toggle */}
        <button
          onClick={() => {
            toggleHighContrast();
            speakText(highContrast ? "High contrast disabled" : "High contrast enabled");
          }}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border transition-colors ${
            highContrast
              ? 'bg-yellow-400 text-black border-yellow-300 font-bold'
              : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
          }`}
          aria-pressed={highContrast}
          title="Toggle high contrast color mode"
        >
          <Contrast className="w-3.5 h-3.5" aria-hidden="true" />
          <span>High Contrast</span>
        </button>

        {/* Font Scaling Buttons */}
        <div className="flex items-center bg-slate-800 rounded border border-slate-700 overflow-hidden" role="group" aria-label="Text sizing">
          <button
            onClick={() => {
              decreaseFontScale();
              speakText("Text size reduced");
            }}
            disabled={fontScale <= 0.9}
            className="px-2 py-1 hover:bg-slate-700 text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed font-medium"
            title="Decrease text size"
          >
            A-
          </button>
          <span className="px-2 py-1 text-teal-300 text-xs font-mono font-semibold border-x border-slate-700">
            {Math.round(fontScale * 100)}%
          </span>
          <button
            onClick={() => {
              increaseFontScale();
              speakText("Text size increased");
            }}
            disabled={fontScale >= 1.3}
            className="px-2 py-1 hover:bg-slate-700 text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed font-bold"
            title="Increase text size"
          >
            A+
          </button>
        </div>

        {/* Reduced Motion Toggle */}
        <button
          onClick={() => {
            toggleReducedMotion();
            speakText(reducedMotion ? "Standard animation enabled" : "Reduced motion enabled");
          }}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border transition-colors ${
            reducedMotion
              ? 'bg-teal-500 text-slate-900 border-teal-400 font-bold'
              : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
          }`}
          aria-pressed={reducedMotion}
          title="Toggle reduced motion for vestibular safety"
        >
          <FastForward className="w-3.5 h-3.5" aria-hidden="true" />
          <span>{reducedMotion ? 'Reduced Motion: ON' : 'Reduced Motion'}</span>
        </button>

        {/* Speech Audio Toggle */}
        <button
          onClick={toggleSpeech}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border transition-colors ${
            speechEnabled
              ? 'bg-teal-600 text-white border-teal-500 font-semibold'
              : 'bg-slate-800 text-slate-400 border-slate-700'
          }`}
          aria-pressed={speechEnabled}
          title="Toggle spoken audio feedback"
        >
          {speechEnabled ? (
            <Volume2 className="w-3.5 h-3.5 text-teal-200" aria-hidden="true" />
          ) : (
            <VolumeX className="w-3.5 h-3.5" aria-hidden="true" />
          )}
          <span>Speech: {speechEnabled ? 'ON' : 'OFF'}</span>
        </button>
      </div>

      {/* Right: Quick Role Switcher for seamless testing */}
      <div className="flex items-center gap-2">
        <span className="text-slate-400 hidden sm:inline text-xs flex items-center gap-1">
          <UserCheck className="w-3.5 h-3.5 text-slate-400" />
          <span>Switch Persona:</span>
        </span>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => switchRole('teacher')}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              role === 'teacher'
                ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
            }`}
          >
            Teacher
          </button>
          <button
            onClick={() => switchRole('student', 1)}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              role === 'student' && user?.email === 'leo@ableconnect.org'
                ? 'bg-cyan-400 text-slate-950 font-bold shadow-sm'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
            }`}
          >
            Student (Leo)
          </button>
          <button
            onClick={() => switchRole('student', 2)}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              role === 'student' && user?.email === 'maya@ableconnect.org'
                ? 'bg-purple-400 text-slate-950 font-bold shadow-sm'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
            }`}
          >
            Student (Maya)
          </button>
          <button
            onClick={() => switchRole('guardian')}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              role === 'guardian'
                ? 'bg-amber-400 text-slate-950 font-bold shadow-sm'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
            }`}
          >
            Guardian
          </button>
        </div>
      </div>
    </div>
  );
};
