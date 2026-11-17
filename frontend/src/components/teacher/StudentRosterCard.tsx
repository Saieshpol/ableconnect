import React from 'react';
import { StudentCard } from '../../types';
import { Sparkles, MessageSquare, AlertCircle, ChevronRight, User } from 'lucide-react';

interface StudentRosterCardProps {
  student: StudentCard;
  onSelect: (student: StudentCard) => void;
}

export const StudentRosterCard: React.FC<StudentRosterCardProps> = ({ student, onSelect }) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between group hover:border-teal-500/50">
      <div>
        {/* Header: Avatar, Name, Pending alert */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-lg text-white shadow-sm ${
              student.avatar_color === 'teal'
                ? 'bg-gradient-to-tr from-teal-600 to-cyan-500'
                : student.avatar_color === 'purple'
                ? 'bg-gradient-to-tr from-purple-600 to-pink-500'
                : 'bg-gradient-to-tr from-amber-600 to-yellow-500'
            }`}>
              {student.full_name.charAt(0)}
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900 group-hover:text-teal-700 transition-colors">
                {student.full_name}
              </h3>
              <span className="text-xs text-slate-500 font-mono">
                {student.student_code}
              </span>
            </div>
          </div>

          {student.pending_request_count > 0 && (
            <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-100 text-amber-900 text-xs font-bold animate-pulse">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
              <span>{student.pending_request_count} Request</span>
            </span>
          )}
        </div>

        {/* Classes pill */}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {student.classes.map((cls, idx) => (
            <span
              key={idx}
              className="text-[11px] font-medium bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-lg border border-slate-200"
            >
              {cls}
            </span>
          ))}
        </div>

        {/* Communication Method */}
        <div className="bg-teal-50/60 border border-teal-100 rounded-xl p-2.5 mb-3">
          <div className="text-[10px] font-bold uppercase tracking-wider text-teal-800 flex items-center gap-1 mb-1">
            <Sparkles className="w-3 h-3 text-teal-600" />
            <span>Preferred Communication</span>
          </div>
          <p className="text-xs font-semibold text-slate-800">
            {student.preferred_communication}
          </p>
        </div>

        {/* Top Teacher Instruction */}
        {student.key_instruction && (
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-2.5 mb-4">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
              Communication Cue for Teacher
            </div>
            <p className="text-xs text-slate-700 line-clamp-2 italic">
              "{student.key_instruction}"
            </p>
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
        {student.latest_emotion && (
          <span className="text-xs font-medium text-slate-500 flex items-center gap-1 capitalize">
            <span>Feeling:</span>
            <strong className="text-slate-800">{student.latest_emotion}</strong>
          </span>
        )}
        <button
          onClick={() => onSelect(student)}
          className="ml-auto flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-800 hover:bg-teal-50 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <span>View Profile</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
