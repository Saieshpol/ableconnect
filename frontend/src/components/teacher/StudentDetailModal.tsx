import React, { useState, useEffect } from 'react';
import { StudentDetail } from '../../types';
import { api } from '../../services/api';
import {
  X, Sparkles, Volume2, ShieldCheck, Heart, User, CheckCircle2,
  Clock, AlertCircle, Info, Calendar, Phone, BookOpen
} from 'lucide-react';

interface StudentDetailModalProps {
  studentId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export const StudentDetailModal: React.FC<StudentDetailModalProps> = ({ studentId, isOpen, onClose }) => {
  const [student, setStudent] = useState<StudentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!studentId || !isOpen) return;
    const fetchDetail = async () => {
      setIsLoading(true);
      try {
        const data = await api.getStudentDetail(studentId);
        setStudent(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDetail();
  }, [studentId, isOpen]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="student-profile-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto"
    >
      <div className="bg-white rounded-3xl max-w-3xl w-full p-6 sm:p-8 relative border border-slate-200 shadow-2xl my-8 max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        {isLoading || !student ? (
          <div className="py-16 text-center text-slate-400">Loading student profile...</div>
        ) : (
          <div className="space-y-6">
            {/* 1. Header & Basic Info */}
            <div className="flex flex-wrap items-center gap-4 pb-6 border-b border-slate-100">
              <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-teal-600 to-cyan-500 text-white flex items-center justify-center font-extrabold text-2xl shadow-md shadow-teal-500/20">
                {student.full_name.charAt(0)}
              </div>
              <div className="grow">
                <div className="flex items-center gap-2">
                  <h2 id="student-profile-title" className="text-2xl font-extrabold text-slate-900">
                    {student.full_name}
                  </h2>
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200">
                    {student.student_code}
                  </span>
                </div>
                <p className="text-sm text-slate-500 mt-0.5">
                  Assigned Classes: {student.classes.join(', ') || 'General Inclusive'}
                </p>
                {student.emergency_contact && (
                  <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-1 font-medium">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    <span>Emergency Contact: {student.emergency_contact}</span>
                  </p>
                )}
              </div>
            </div>

            {/* 2. DEDICATED SECTION: "How to Communicate With This Student" */}
            <div className="bg-amber-50/70 border-2 border-amber-300/80 rounded-2xl p-5 shadow-xs">
              <div className="flex items-center gap-2 mb-3">
                <div className="p-1.5 bg-amber-200 text-amber-900 rounded-lg">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-base text-amber-950">
                    How to Communicate With This Student
                  </h3>
                  <p className="text-xs text-amber-800">
                    Educator-approved personalized guidelines. Never inferred from diagnosis.
                  </p>
                </div>
              </div>

              <div className="space-y-2 mt-3">
                {student.support_instructions.length > 0 ? (
                  student.support_instructions.map((inst) => (
                    <div
                      key={inst.id}
                      className="bg-white/90 border border-amber-200/90 rounded-xl p-3 flex items-start gap-3 shadow-2xs"
                    >
                      <CheckCircle2 className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                      <div className="grow">
                        <p className="text-xs font-bold text-slate-900">{inst.instruction}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                            {inst.category}
                          </span>
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                            inst.priority === 'essential'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-teal-100 text-teal-800'
                          }`}>
                            {inst.priority}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-amber-800 italic">No specific communication instructions recorded yet.</p>
                )}
              </div>
            </div>

            {/* 3. Communication Preferences Grid */}
            {student.preferences && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
                  <Volume2 className="w-4 h-4 text-teal-600" />
                  <span>Configured Communication Preferences</span>
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                  <div className={`p-3 rounded-xl border ${student.preferences.picture_based_communication ? 'bg-teal-50 border-teal-200 text-teal-900 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'}`}>
                    Picture-Based AAC: {student.preferences.picture_based_communication ? 'Yes' : 'No'}
                  </div>
                  <div className={`p-3 rounded-xl border ${student.preferences.text_to_speech ? 'bg-teal-50 border-teal-200 text-teal-900 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'}`}>
                    Speech Synthesis: {student.preferences.text_to_speech ? 'Active' : 'Off'}
                  </div>
                  <div className={`p-3 rounded-xl border ${student.preferences.written_communication ? 'bg-teal-50 border-teal-200 text-teal-900 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'}`}>
                    Written / Text: {student.preferences.written_communication ? 'Preferred' : 'Secondary'}
                  </div>
                  <div className={`p-3 rounded-xl border ${student.preferences.gestures ? 'bg-teal-50 border-teal-200 text-teal-900 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'}`}>
                    Gestures: {student.preferences.gestures ? 'Accepted' : 'No'}
                  </div>
                  <div className={`p-3 rounded-xl border ${student.preferences.sign_language ? 'bg-teal-50 border-teal-200 text-teal-900 font-bold' : 'bg-slate-50 border-slate-200 text-slate-500'}`}>
                    Sign Language: {student.preferences.sign_language ? 'Yes' : 'No'}
                  </div>
                  <div className="p-3 rounded-xl border bg-slate-50 border-slate-200 text-slate-700">
                    Symbol Size: <strong className="capitalize">{student.preferences.preferred_symbol_size}</strong>
                  </div>
                </div>
              </div>
            )}

            {/* 4. Sensory & Classroom Profile */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-1 flex items-center gap-1.5">
                  <Heart className="w-4 h-4 text-rose-500" />
                  <span>Sensory Accommodations</span>
                </div>
                <p className="text-xs text-slate-700 mt-1">
                  {student.sensory_profile || 'Standard classroom lighting and ambient audio.'}
                </p>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-1 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-indigo-500" />
                  <span>Assistance Level</span>
                </div>
                <p className="text-xs text-slate-700 mt-1 capitalize font-semibold">
                  {student.assistance_level} assistance in group activities.
                </p>
                {student.emergency_notes && (
                  <p className="text-xs text-amber-800 mt-2 font-medium bg-amber-50 p-2 rounded-lg border border-amber-200">
                    Note: {student.emergency_notes}
                  </p>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-sm transition-colors cursor-pointer"
              >
                Close Profile
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
