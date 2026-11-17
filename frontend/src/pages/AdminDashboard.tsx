import React, { useEffect, useState } from 'react';
import { Activity, BookOpen, CheckCircle2, GraduationCap, ShieldCheck, Users, UserRound, Clock3 } from 'lucide-react';
import { api } from '../services/api';
import type { StudentCard } from '../types';

export const AdminDashboard: React.FC = () => {
  const [students, setStudents] = useState<StudentCard[]>([]);
  const [classes, setClasses] = useState<{ id: number; name: string; grade_level: string; student_count: number }[]>([]);
  const [stats, setStats] = useState({ total_students: 0, total_classes: 0, pending_requests: 0, unread_messages: 0, recent_activities: 0 });
  useEffect(() => {
    void Promise.all([api.getStudents(), api.getClasses(), api.getDashboardStats()]).then(([s, c, d]) => {
      setStudents(s); setClasses(c); setStats(d);
    });
  }, []);
  const cards = [
    { label: 'Students', value: stats.total_students || students.length, icon: Users, color: 'text-teal-700 bg-teal-50' },
    { label: 'Classes', value: stats.total_classes || classes.length, icon: BookOpen, color: 'text-blue-700 bg-blue-50' },
    { label: 'Teachers', value: '—', icon: GraduationCap, color: 'text-violet-700 bg-violet-50' },
    { label: 'Pending requests', value: stats.pending_requests, icon: Clock3, color: 'text-amber-700 bg-amber-50' },
  ];
  return <div className="min-h-[75vh] bg-slate-50 px-4 py-8 sm:px-8">
    <div className="mx-auto max-w-7xl">
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div><div className="mb-2 inline-flex items-center gap-2 rounded-full bg-violet-100 px-3 py-1 text-xs font-bold text-violet-800"><ShieldCheck size={15}/> Administration</div><h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Platform overview</h1><p className="mt-1 text-sm text-slate-600">A clear view of AbleConnect’s learning community.</p></div>
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600"><span className="font-semibold text-slate-900">System status</span><span className="ml-3 inline-flex items-center gap-1.5 text-emerald-700"><CheckCircle2 size={15}/>Operational</span></div>
      </div>
      <section aria-label="Platform metrics" className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">{cards.map(({label,value,icon:Icon,color}) => <article key={label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><span className="text-sm font-medium text-slate-600">{label}</span><span className={`rounded-xl p-2 ${color}`}><Icon size={19}/></span></div><p className="mt-4 text-3xl font-bold text-slate-900">{value}</p><p className="mt-1 text-xs text-slate-500">Across the platform</p></article>)}</section>
      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm" aria-labelledby="students-heading"><div className="flex items-center justify-between border-b border-slate-100 px-5 py-4"><div><h2 id="students-heading" className="font-bold text-slate-900">Student directory</h2><p className="text-xs text-slate-500">Account status and classroom assignment</p></div><Users size={19} className="text-slate-400"/></div><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr><th scope="col" className="px-5 py-3">Student</th><th scope="col" className="px-5 py-3">Class</th><th scope="col" className="px-5 py-3">Account</th></tr></thead><tbody className="divide-y divide-slate-100">{students.slice(0,6).map(s=><tr key={s.id}><td className="px-5 py-3"><span className="font-semibold text-slate-800">{s.full_name}</span><span className="block text-xs text-slate-500">{s.student_code}</span></td><td className="px-5 py-3 text-slate-600">{s.classes?.join(', ') || 'Unassigned'}</td><td className="px-5 py-3"><span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">Active</span></td></tr>)}{students.length===0 && <tr><td colSpan={3} className="px-5 py-8 text-center text-slate-500">Student records are unavailable.</td></tr>}</tbody></table></div></section>
        <div className="space-y-6"><section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><div className="mb-4 flex items-center gap-2"><BookOpen size={18} className="text-blue-700"/><h2 className="font-bold text-slate-900">Classes</h2></div><ul className="space-y-3">{classes.slice(0,5).map(c=><li key={c.id} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-3"><span className="font-medium text-slate-800">{c.name}<span className="ml-2 text-xs text-slate-500">{c.grade_level}</span></span><span className="text-xs text-slate-500">{c.student_count} students</span></li>)}{classes.length===0&&<li className="text-sm text-slate-500">No class records available.</li>}</ul></section><section className="rounded-2xl border border-teal-100 bg-teal-50/70 p-5"><div className="flex items-center gap-2"><Activity size={18} className="text-teal-700"/><h2 className="font-bold text-slate-900">Privacy and access</h2></div><p className="mt-2 text-sm leading-relaxed text-slate-700">Student support information is personal. Access is tied to assigned roles and should only be used to support each learner.</p><div className="mt-4 flex items-center gap-2 text-xs font-semibold text-teal-800"><UserRound size={15}/>Role-based workspace</div></section></div>
      </div>
    </div>
  </div>;
};
