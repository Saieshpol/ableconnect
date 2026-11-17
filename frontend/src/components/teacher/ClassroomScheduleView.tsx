import React, { useState, useEffect } from 'react';
import { ScheduleItem } from '../../types';
import { api } from '../../services/api';
import {
  Calendar, Clock, Sun, BookOpen, Coffee, Palette, Calculator,
  FlaskConical, CheckCircle2
} from 'lucide-react';

interface ClassroomScheduleViewProps {
  isStudentMode?: boolean;
}

export const ClassroomScheduleView: React.FC<ClassroomScheduleViewProps> = ({ isStudentMode = false }) => {
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const data = await api.getSchedule();
        setSchedule(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSchedule();
  }, []);

  const renderIcon = (iconName: string) => {
    switch (iconName) {
      case 'sun': return <Sun className="w-5 h-5 text-amber-500" />;
      case 'flask-conical': return <FlaskConical className="w-5 h-5 text-indigo-500" />;
      case 'coffee': return <Coffee className="w-5 h-5 text-teal-500" />;
      case 'calculator': return <Calculator className="w-5 h-5 text-blue-500" />;
      case 'palette': return <Palette className="w-5 h-5 text-purple-500" />;
      default: return <BookOpen className="w-5 h-5 text-slate-500" />;
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Loading daily schedule...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-extrabold text-lg text-slate-900 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-teal-600" />
            <span>Today's Visual Schedule</span>
          </h3>
          <p className="text-xs text-slate-500">
            {isStudentMode ? 'Follow along with each period in your day.' : 'Classroom timetable with visual support cues.'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {schedule.map((item) => (
          <div
            key={item.id}
            className={`p-4 rounded-2xl border-2 transition-all flex flex-col justify-between ${
              item.is_current
                ? 'bg-teal-50 border-teal-500 shadow-md ring-2 ring-teal-500/20'
                : 'bg-white border-slate-200 shadow-2xs'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="flex items-center gap-1.5 text-xs font-bold text-slate-500">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{item.start_time} - {item.end_time}</span>
                </span>
                {item.is_current && (
                  <span className="px-2 py-0.5 rounded-full bg-teal-600 text-white text-[10px] font-extrabold uppercase tracking-wider animate-pulse">
                    Current Period
                  </span>
                )}
              </div>

              <div className="flex items-center gap-3 my-2">
                <div className="p-2.5 bg-slate-100 rounded-xl">
                  {renderIcon(item.visual_icon)}
                </div>
                <div>
                  <h4 className="font-extrabold text-base text-slate-900 leading-snug">
                    {item.subject}
                  </h4>
                  <p className="text-xs text-slate-500 font-medium">{item.period_name}</p>
                </div>
              </div>

              {item.instructions && (
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-600 mt-2">
                  <span className="font-semibold text-slate-700">Guide: </span>
                  {item.instructions}
                </div>
              )}
            </div>

            {item.room && (
              <div className="pt-2 mt-2 border-t border-slate-100 text-[11px] text-slate-400 font-medium">
                Location: {item.room}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
