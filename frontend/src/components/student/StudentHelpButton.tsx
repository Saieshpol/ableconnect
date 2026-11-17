import React, { useState } from 'react';
import { api } from '../../services/api';
import { speech } from '../../services/speech';
import { LifeBuoy, Coffee, HelpCircle, AlertCircle, Clock, CheckCircle2, ChevronRight } from 'lucide-react';
import { StudentRequest } from '../../types';

interface StudentHelpButtonProps {
  onRequestSent?: (req: StudentRequest) => void;
}

export const StudentHelpButton: React.FC<StudentHelpButtonProps> = ({ onRequestSent }) => {
  const [activeRequest, setActiveRequest] = useState<StudentRequest | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const helpOptions = [
    { type: 'help', label: 'I need help', icon: <LifeBuoy className="w-6 h-6 text-amber-600" />, phrase: "I need help with my work." },
    { type: 'break', label: 'I need a break', icon: <Coffee className="w-6 h-6 text-teal-600" />, phrase: "I need a short break." },
    { type: 'dont_understand', label: "I don't understand", icon: <HelpCircle className="w-6 h-6 text-indigo-600" />, phrase: "I do not understand this step." },
    { type: 'uncomfortable', label: 'I feel uncomfortable', icon: <AlertCircle className="w-6 h-6 text-rose-600" />, phrase: "I feel uncomfortable right now." },
  ];

  const handleSendHelp = async (option: typeof helpOptions[0]) => {
    speech.speak(option.phrase);
    setIsSubmitting(true);
    try {
      const res = await api.submitRequest(option.type, option.phrase);
      setActiveRequest(res);
      if (onRequestSent) onRequestSent(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-extrabold text-lg sm:text-xl text-slate-900 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-teal-500 animate-ping" />
            <span>Assistance Requests</span>
          </h3>
          <p className="text-xs sm:text-sm text-slate-500">
            Tap an option below to notify your teacher.
          </p>
        </div>
        {activeRequest && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-xs font-bold">
            <span className="text-slate-500 uppercase tracking-wider text-[10px]">Status:</span>
            <span className={`capitalize px-2 py-0.5 rounded-md ${
              activeRequest.status === 'sent'
                ? 'bg-amber-100 text-amber-800'
                : activeRequest.status === 'seen'
                ? 'bg-blue-100 text-blue-800'
                : 'bg-emerald-100 text-emerald-800'
            }`}>
              {activeRequest.status}
            </span>
          </div>
        )}
      </div>

      {/* Grid of Dignified Touch-friendly Request Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {helpOptions.map((opt) => (
          <button
            key={opt.type}
            onClick={() => handleSendHelp(opt)}
            disabled={isSubmitting}
            className="flex items-center justify-between p-4 rounded-2xl border-2 border-slate-200 hover:border-teal-500 bg-slate-50 hover:bg-teal-50/40 text-left transition-all active:scale-98 group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="p-3 bg-white rounded-xl shadow-xs group-hover:scale-110 transition-transform">
                {opt.icon}
              </div>
              <div>
                <span className="font-extrabold text-base text-slate-900 block">
                  {opt.label}
                </span>
                <span className="text-xs text-slate-500">
                  {opt.phrase}
                </span>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-teal-600 transition-colors" />
          </button>
        ))}
      </div>

      {activeRequest && (
        <div className="p-3 bg-teal-50/80 rounded-2xl border border-teal-200 flex items-center justify-between text-xs text-teal-900">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600" />
            <span>
              Request sent: <strong>{activeRequest.message}</strong>
            </span>
          </div>
          <span className="text-[11px] text-teal-700 font-semibold">Teacher informed</span>
        </div>
      )}
    </div>
  );
};
