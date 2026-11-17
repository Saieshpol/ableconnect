import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { StudentDetail, SupportInstruction } from '../types';
import {
  Shield, CheckCircle2, Heart, Volume2, MessageSquare,
  Award, Send, Info, Phone, Calendar
} from 'lucide-react';

export const GuardianPortal: React.FC = () => {
  const [student, setStudent] = useState<StudentDetail | null>(null);
  const [messageText, setMessageText] = useState('');
  const [sentNotice, setSentNotice] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLinkedChild = async () => {
      try {
        // David Chen is authorized for Leo Vance (student_id: 1)
        const data = await api.getStudentDetail(1);
        setStudent(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLinkedChild();
  }, []);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageText.trim()) return;
    setSentNotice(true);
    setMessageText('');
    setTimeout(() => setSentNotice(false), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* 1. Guardian Header Banner */}
      <div className="bg-gradient-to-r from-amber-600 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-amber-400/20 text-amber-300 text-xs font-bold border border-amber-400/30 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5" />
              <span>Authorized Guardian Workspace</span>
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            David Chen
          </h1>
          <p className="text-xs sm:text-sm text-amber-200 mt-1">
            Authorized Parent / Guardian for <strong>Leo Vance</strong> (STU-0101)
          </p>
        </div>

        <div className="text-right">
          <span className="text-xs text-amber-200 block">Lead Educator:</span>
          <span className="text-sm font-bold text-white">Sarah Jenkins, M.Ed. (Room 102)</span>
        </div>
      </div>

      {isLoading || !student ? (
        <div className="p-12 text-center text-slate-400">Loading student collaboration data...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column: Student Summary & Support Strategies */}
          <div className="md:col-span-2 space-y-6">
            {/* Approved Communication Guidance */}
            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-amber-50 text-amber-700 rounded-xl">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-extrabold text-slate-900">
                    Approved Communication Strategies
                  </h2>
                  <p className="text-xs text-slate-500">
                    Co-developed with educators for home and school consistency.
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                {student.support_instructions.map((inst: SupportInstruction) => (
                  <div key={inst.id} className="p-3.5 rounded-2xl bg-amber-50/50 border border-amber-200 text-xs">
                    <p className="font-bold text-slate-900">{inst.instruction}</p>
                    <span className="text-[10px] text-amber-800 font-semibold uppercase mt-1 block">
                      Category: {inst.category} • Priority: {inst.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Individual Growth Milestones */}
            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-teal-50 text-teal-700 rounded-xl">
                  <Award className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-extrabold text-slate-900">
                    Learning & Communication Goals
                  </h2>
                  <p className="text-xs text-slate-500">
                    Individual milestone progress.
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex justify-between text-xs font-bold text-slate-800">
                  <span>Visual AAC 2-Card Sentence Construction</span>
                  <span className="text-teal-700">75% Achieved</span>
                </div>
                <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                  <div className="bg-teal-600 h-full rounded-full" style={{ width: '75%' }} />
                </div>
                <p className="text-xs text-slate-500">
                  Leo is successfully requesting breaks and assistance independently during classroom sessions.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Direct Educator Messaging */}
          <div className="space-y-6">
            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-indigo-50 text-indigo-700 rounded-xl">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">
                    Message Sarah Jenkins
                  </h3>
                  <p className="text-xs text-slate-500">
                    Private teacher communication
                  </p>
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs text-slate-700 italic">
                "Leo participated enthusiastically in today's science observation journal! His focus was fantastic."
                <span className="text-[10px] text-slate-400 block mt-1 not-italic font-bold">
                  — Sarah Jenkins, Today 11:30 AM
                </span>
              </div>

              {sentNotice && (
                <div className="p-2.5 bg-emerald-50 text-emerald-800 rounded-xl text-xs font-bold text-center border border-emerald-200">
                  Note sent to Ms. Jenkins!
                </div>
              )}

              <form onSubmit={handleSendMessage} className="space-y-3">
                <textarea
                  rows={3}
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  placeholder="Share a note or update for tomorrow..."
                  className="w-full p-3 border border-slate-300 rounded-2xl text-xs focus:ring-2 focus:ring-teal-500 outline-none"
                />
                <button
                  type="submit"
                  disabled={!messageText.trim()}
                  className="w-full py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Send Message</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
