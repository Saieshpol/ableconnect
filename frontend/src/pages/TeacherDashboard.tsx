import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  StudentCard, Classroom, StudentRequest, DashboardStats
} from '../types';
import { StudentRosterCard } from '../components/teacher/StudentRosterCard';
import { StudentDetailModal } from '../components/teacher/StudentDetailModal';
import { InstructionSimplifierModal } from '../components/teacher/InstructionSimplifierModal';
import { ClassroomScheduleView } from '../components/teacher/ClassroomScheduleView';
import {
  LayoutDashboard, Users, BookOpen, MessageSquare, Award,
  Sparkles, Settings, Plus, Search, Filter, AlertCircle,
  CheckCircle2, Clock, Calendar, Check, Send, PhoneCall, RefreshCw
} from 'lucide-react';

export const TeacherDashboard: React.FC = () => {
  const [activeSection, setActiveSection] = useState<
    'overview' | 'classes' | 'students' | 'communication' | 'progress' | 'activities' | 'parents' | 'settings'
  >('overview');

  const [stats, setStats] = useState<DashboardStats>({
    total_students: 3,
    total_classes: 2,
    pending_requests: 1,
    unread_messages: 1,
    recent_activities: 1,
  });

  const [students, setStudents] = useState<StudentCard[]>([]);
  const [classes, setClasses] = useState<Classroom[]>([]);
  const [requests, setRequests] = useState<StudentRequest[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isSimplifierOpen, setIsSimplifierOpen] = useState(false);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClassFilter, setSelectedClassFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  // New Class Form State
  const [showAddClass, setShowAddClass] = useState(false);
  const [newClassName, setNewClassName] = useState('');
  const [newClassGrade, setNewClassGrade] = useState('Grade 3');
  const [newClassRoom, setNewClassRoom] = useState('Room 102');

  const loadAllData = async () => {
    setIsLoading(true);
    try {
      const [fetchedStats, fetchedStudents, fetchedClasses, fetchedRequests] = await Promise.all([
        api.getDashboardStats(),
        api.getStudents(),
        api.getClasses(),
        api.getRequests(),
      ]);
      setStats(fetchedStats);
      setStudents(fetchedStudents);
      setClasses(fetchedClasses);
      setRequests(fetchedRequests);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleSelectStudent = (student: StudentCard) => {
    setSelectedStudentId(student.id);
    setIsDetailOpen(true);
  };

  const handleUpdateRequestStatus = async (requestId: number, status: 'seen' | 'responded') => {
    try {
      await api.updateRequestStatus(requestId, status, status === 'responded' ? 'Acknowledged and supported' : undefined);
      loadAllData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassName.trim()) return;
    try {
      await api.createClass({
        name: newClassName,
        grade_level: newClassGrade,
        room: newClassRoom,
      });
      setShowAddClass(false);
      setNewClassName('');
      loadAllData();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredStudents = students.filter((s) => {
    const matchesSearch = s.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          s.student_code.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesClass = selectedClassFilter === 'all' || s.classes.includes(selectedClassFilter);
    return matchesSearch && matchesClass;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* 1. Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-gradient-to-r from-teal-800 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 text-xs font-bold border border-teal-500/30">
              Specialized Educator Portal
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Sarah Jenkins, M.Ed.
          </h1>
          <p className="text-xs sm:text-sm text-teal-200 mt-1">
            Oakridge Elementary Inclusive Academy • Room 102
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSimplifierOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-sm transition-all cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            <span>Instruction Simplifier</span>
          </button>
          <button
            onClick={loadAllData}
            className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. Top Navigation Tabs (Main 8 Sections) */}
      <div className="flex overflow-x-auto gap-2 pb-2 border-b border-slate-200" role="tablist">
        {[
          { id: 'overview', label: 'Overview', icon: <LayoutDashboard className="w-4 h-4" /> },
          { id: 'classes', label: 'My Classes', icon: <BookOpen className="w-4 h-4" /> },
          { id: 'students', label: 'Students', icon: <Users className="w-4 h-4" /> },
          { id: 'communication', label: 'Communication Center', icon: <MessageSquare className="w-4 h-4" />, count: requests.filter(r => r.status === 'sent').length },
          { id: 'progress', label: 'Student Progress', icon: <Award className="w-4 h-4" /> },
          { id: 'activities', label: 'Classroom Activities', icon: <Calendar className="w-4 h-4" /> },
          { id: 'parents', label: 'Parent Communication', icon: <PhoneCall className="w-4 h-4" /> },
          { id: 'settings', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
        ].map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeSection === tab.id}
            onClick={() => setActiveSection(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
              activeSection === tab.id
                ? 'bg-slate-900 text-white shadow-xs'
                : 'bg-white hover:bg-slate-100 text-slate-600 border border-slate-200'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
            {tab.count !== undefined && tab.count > 0 && (
              <span className="px-1.5 py-0.5 rounded-full bg-amber-500 text-slate-950 text-[10px] font-extrabold">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* 3. Section Content Rendering */}

      {/* SECTION 1: OVERVIEW */}
      {activeSection === 'overview' && (
        <div className="space-y-8">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Students</span>
              <div className="text-3xl font-extrabold text-slate-900 mt-2">{stats.total_students}</div>
              <span className="text-[11px] text-teal-600 font-semibold mt-1 block">Active Profiles</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Classrooms</span>
              <div className="text-3xl font-extrabold text-slate-900 mt-2">{stats.total_classes}</div>
              <span className="text-[11px] text-indigo-600 font-semibold mt-1 block">Inclusive Sections</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Pending Requests</span>
              <div className="text-3xl font-extrabold text-amber-600 mt-2">{stats.pending_requests}</div>
              <span className="text-[11px] text-amber-700 font-semibold mt-1 block">Requires Attention</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Unread Messages</span>
              <div className="text-3xl font-extrabold text-teal-600 mt-2">{stats.unread_messages}</div>
              <span className="text-[11px] text-teal-700 font-semibold mt-1 block">Student & Guardian</span>
            </div>
          </div>

          {/* Pending Assistance Requests Alert Bar */}
          {requests.filter(r => r.status === 'sent' || r.status === 'seen').length > 0 && (
            <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-amber-600" />
                  <h3 className="font-extrabold text-base text-amber-950">
                    Live Student Assistance Requests ({requests.filter(r => r.status === 'sent' || r.status === 'seen').length})
                  </h3>
                </div>
                <button
                  onClick={() => setActiveSection('communication')}
                  className="text-xs font-bold text-amber-900 hover:underline"
                >
                  View All Requests →
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {requests.filter(r => r.status === 'sent' || r.status === 'seen').slice(0, 2).map((req) => (
                  <div key={req.id} className="bg-white rounded-xl p-3 border border-amber-200 flex items-center justify-between gap-3 shadow-2xs">
                    <div>
                      <div className="text-xs font-bold text-slate-900">
                        {req.student_name}
                      </div>
                      <p className="text-xs text-slate-600 font-medium">
                        "{req.message || req.request_type}"
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {req.status === 'sent' && (
                        <button
                          onClick={() => handleUpdateRequestStatus(req.id, 'seen')}
                          className="px-2.5 py-1 rounded-lg bg-blue-100 hover:bg-blue-200 text-blue-900 font-bold text-xs transition-colors"
                        >
                          Mark Seen
                        </button>
                      )}
                      <button
                        onClick={() => handleUpdateRequestStatus(req.id, 'responded')}
                        className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition-colors"
                      >
                        Respond
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Schedule Component Integration */}
          <ClassroomScheduleView />

          {/* Student Roster Quick Preview */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-extrabold text-lg text-slate-900">
                  Student Roster & Communication Preferences
                </h3>
                <p className="text-xs text-slate-500">
                  Configured support instructions and preferred interaction modes.
                </p>
              </div>
              <button
                onClick={() => setActiveSection('students')}
                className="text-xs font-bold text-teal-700 hover:text-teal-800"
              >
                Browse All Students →
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {students.slice(0, 3).map((student) => (
                <StudentRosterCard
                  key={student.id}
                  student={student}
                  onSelect={handleSelectStudent}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SECTION 2: MY CLASSES */}
      {activeSection === 'classes' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-slate-900">My Classes & Rosters</h2>
              <p className="text-xs text-slate-500">Organize inclusive classrooms and student groupings.</p>
            </div>
            <button
              onClick={() => setShowAddClass(true)}
              className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold rounded-xl transition-all cursor-pointer shadow-xs"
            >
              <Plus className="w-4 h-4" />
              <span>Create Class</span>
            </button>
          </div>

          {/* Add Class Modal / Inline */}
          {showAddClass && (
            <form onSubmit={handleCreateClass} className="bg-slate-50 p-5 rounded-2xl border border-slate-300 space-y-4 max-w-lg">
              <h3 className="text-sm font-bold text-slate-900">New Classroom Setup</h3>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Class Name</label>
                  <input
                    type="text"
                    value={newClassName}
                    onChange={(e) => setNewClassName(e.target.value)}
                    required
                    placeholder="e.g. Science Lab 4"
                    className="w-full p-2 border border-slate-300 rounded-xl text-xs bg-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Grade Level</label>
                  <input
                    type="text"
                    value={newClassGrade}
                    onChange={(e) => setNewClassGrade(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded-xl text-xs bg-white"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddClass(false)}
                  className="px-3 py-1.5 rounded-lg border text-xs font-semibold text-slate-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-teal-600 text-white text-xs font-bold"
                >
                  Save Class
                </button>
              </div>
            </form>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {classes.map((c) => (
              <div key={c.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-teal-100 text-teal-800">
                      {c.grade_level}
                    </span>
                    <h3 className="font-extrabold text-lg text-slate-900 mt-1">{c.name}</h3>
                    <p className="text-xs text-slate-500">{c.room || 'Room 102'}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-black text-slate-900">{c.student_count}</span>
                    <span className="text-[10px] text-slate-500 block">Enrolled</span>
                  </div>
                </div>
                <div className="pt-3 border-t border-slate-100 text-xs text-slate-600">
                  Schedule: {c.schedule_summary || 'Mon-Fri 08:30 - 14:45'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 3: STUDENTS */}
      {activeSection === 'students' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-extrabold text-slate-900">Student Profiles & Needs</h2>
              <p className="text-xs text-slate-500">
                Personalized communication preferences and educator support guidelines.
              </p>
            </div>

            {/* Search & Filter */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search student..."
                  className="pl-9 pr-3 py-1.5 border border-slate-300 rounded-xl text-xs bg-white focus:ring-2 focus:ring-teal-500 outline-none w-48 sm:w-60"
                />
              </div>

              <select
                value={selectedClassFilter}
                onChange={(e) => setSelectedClassFilter(e.target.value)}
                className="px-3 py-1.5 border border-slate-300 rounded-xl text-xs bg-white text-slate-700"
              >
                <option value="all">All Classes</option>
                {classes.map(c => (
                  <option key={c.id} value={c.name}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {filteredStudents.map((student) => (
              <StudentRosterCard
                key={student.id}
                student={student}
                onSelect={handleSelectStudent}
              />
            ))}
          </div>
        </div>
      )}

      {/* SECTION 4: COMMUNICATION CENTER */}
      {activeSection === 'communication' && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900">Student Communication Center</h2>
            <p className="text-xs text-slate-500">
              Live assistance requests and incoming AAC picture messages from students.
            </p>
          </div>

          <div className="space-y-3">
            {requests.length === 0 ? (
              <p className="text-slate-400 text-sm italic py-8 text-center">No active student requests.</p>
            ) : (
              requests.map((req) => (
                <div
                  key={req.id}
                  className={`bg-white rounded-2xl border p-4 flex flex-wrap items-center justify-between gap-4 transition-all ${
                    req.status === 'sent'
                      ? 'border-amber-400 shadow-sm ring-1 ring-amber-400/20'
                      : 'border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded-xl ${
                      req.status === 'sent' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                    }`}>
                      <AlertCircle className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-sm text-slate-900">{req.student_name}</span>
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${
                          req.status === 'sent' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                        }`}>
                          {req.status}
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 mt-0.5 font-medium">"{req.message}"</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">
                        Received: {new Date(req.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {req.status === 'sent' && (
                      <button
                        onClick={() => handleUpdateRequestStatus(req.id, 'seen')}
                        className="px-3 py-1.5 rounded-xl bg-blue-50 text-blue-800 border border-blue-200 hover:bg-blue-100 font-bold text-xs transition-colors"
                      >
                        Acknowledge (Seen)
                      </button>
                    )}
                    {req.status !== 'resolved' && req.status !== 'responded' && (
                      <button
                        onClick={() => handleUpdateRequestStatus(req.id, 'responded')}
                        className="px-4 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-xs transition-colors"
                      >
                        Mark Responded
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* SECTION 5: STUDENT PROGRESS */}
      {activeSection === 'progress' && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900">Individual Milestone & Goal Tracking</h2>
            <p className="text-xs text-slate-500">
              Non-comparative growth. Progress is measured strictly against individual goals, never ranked against peers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-extrabold text-sm text-slate-900">Leo Vance (AAC)</span>
                <span className="text-xs font-bold text-teal-700">75% Achieved</span>
              </div>
              <p className="text-xs text-slate-600">Goal: Communicates immediate physiological needs using 2-card AAC sequence.</p>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div className="bg-teal-600 h-full rounded-full" style={{ width: '75%' }} />
              </div>
              <span className="text-[11px] text-slate-400 block">Baseline: 1 single-card request per day. Currently: 4 requests independently.</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-extrabold text-sm text-slate-900">Maya Patel (Step-by-Step)</span>
                <span className="text-xs font-bold text-indigo-700">80% Achieved</span>
              </div>
              <p className="text-xs text-slate-600">Goal: Completes 3-step written sequence without requiring repeat verbal prompts.</p>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div className="bg-indigo-600 h-full rounded-full" style={{ width: '80%' }} />
              </div>
              <span className="text-[11px] text-slate-400 block">Accompanied by Simplified Instructions tool checklist.</span>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 6: CLASSROOM ACTIVITIES */}
      {activeSection === 'activities' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-slate-900">Inclusive Classroom Activities</h2>
              <p className="text-xs text-slate-500">Activities with step-by-step plain-language instructions.</p>
            </div>
            <button
              onClick={() => setIsSimplifierOpen(true)}
              className="px-4 py-2 bg-teal-600 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-xs"
            >
              <Sparkles className="w-4 h-4" />
              <span>Simplify New Assignment</span>
            </button>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-teal-100 text-teal-800">Science</span>
              <span className="text-xs text-slate-500">Target Skills: Observation, Fine Motor</span>
            </div>
            <h3 className="font-extrabold text-base text-slate-900">Plant Seedling Observation Journal</h3>
            <p className="text-xs text-slate-600">Look closely at your seedling. Record leaf count and draw the root structure.</p>
            <div className="pt-2 border-t border-slate-100 space-y-1.5 text-xs text-slate-700 font-semibold">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-[10px]">1</span>
                <span>Pick up your seedling cup.</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-[10px]">2</span>
                <span>Count the green leaves.</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-[10px]">3</span>
                <span>Draw the shape of the leaf in your journal.</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 7: PARENT COMMUNICATION */}
      {activeSection === 'parents' && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900">Guardian Collaboration</h2>
            <p className="text-xs text-slate-500">Authorized parent updates and communication preference sign-offs.</p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-lg shrink-0">
              D
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base text-slate-900">David Chen</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-100 text-amber-800">
                  Parent of Leo Vance
                </span>
              </div>
              <p className="text-xs text-slate-600">
                Contact: +1 (555) 234-5678 • Preferred: Email
              </p>
              <p className="text-xs text-slate-700 bg-slate-50 p-2 rounded-xl border border-slate-200 mt-2 italic">
                "Leo had a great week with his sound defenders. Thank you for providing the 2-minute visual cue before recess!"
              </p>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 8: SETTINGS */}
      {activeSection === 'settings' && (
        <div className="space-y-6 max-w-xl">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900">Classroom Settings & Accessibility</h2>
            <p className="text-xs text-slate-500">Configure accessibility defaults and notification thresholds.</p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-bold text-xs text-slate-900">Visual Request Alert Sound</span>
                <p className="text-[11px] text-slate-500">Gentle chime when a student presses the Help button.</p>
              </div>
              <input type="checkbox" defaultChecked className="accent-teal-600 w-4 h-4 cursor-pointer" />
            </div>

            <div className="flex items-center justify-between border-t border-slate-100 pt-3">
              <div>
                <span className="font-bold text-xs text-slate-900">Strict Privacy Masking</span>
                <p className="text-[11px] text-slate-500">Hide individual support tags during class projector casting.</p>
              </div>
              <input type="checkbox" defaultChecked className="accent-teal-600 w-4 h-4 cursor-pointer" />
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      <StudentDetailModal
        studentId={selectedStudentId}
        isOpen={isDetailOpen}
        onClose={() => {
          setIsDetailOpen(false);
          setSelectedStudentId(null);
        }}
      />

      <InstructionSimplifierModal
        isOpen={isSimplifierOpen}
        onClose={() => setIsSimplifierOpen(false)}
      />
    </div>
  );
};
