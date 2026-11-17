import {
  AuthResponse, User, StudentCard, StudentDetail, Classroom,
  CommunicationBoard, StudentRequest, EmotionCheckin, ScheduleItem,
  SimplifyResult, DashboardStats
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    const token = localStorage.getItem('ableconnect_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Login failed');
    }
    const data: AuthResponse = await res.json();
    localStorage.setItem('ableconnect_token', data.access_token);
    return data;
  }

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Session invalid');
    return res.json();
  }

  async demoSwitch(targetRole: string, studentId?: number): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/demo-switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_role: targetRole, student_id: studentId }),
    });
    if (!res.ok) throw new Error('Failed to switch demo account');
    const data: AuthResponse = await res.json();
    localStorage.setItem('ableconnect_token', data.access_token);
    return data;
  }

  // Classes
  async getClasses(): Promise<Classroom[]> {
    const res = await fetch(`${API_BASE}/classes`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  }

  async createClass(payload: { name: string; grade_level: string; room?: string; color_theme?: string }): Promise<Classroom> {
    const res = await fetch(`${API_BASE}/classes`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to create class');
    return res.json();
  }

  // Students
  async getStudents(): Promise<StudentCard[]> {
    const res = await fetch(`${API_BASE}/students`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  }

  async getStudentDetail(id: number): Promise<StudentDetail> {
    const res = await fetch(`${API_BASE}/students/${id}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Student not found');
    return res.json();
  }

  async getStudentSelf(): Promise<StudentDetail> {
    const res = await fetch(`${API_BASE}/students/me`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Student profile not found');
    return res.json();
  }

  // Communication & AAC
  async getBoards(): Promise<CommunicationBoard[]> {
    const res = await fetch(`${API_BASE}/communication/boards`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  }

  async synthesizeSentence(symbols: string[]): Promise<{ sentence: string; spoken_text: string }> {
    const res = await fetch(`${API_BASE}/communication/synthesize-sentence`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ symbols }),
    });
    if (!res.ok) throw new Error('Failed to synthesize sentence');
    return res.json();
  }

  async submitRequest(requestType: string, message?: string): Promise<StudentRequest> {
    const res = await fetch(`${API_BASE}/communication/requests`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ request_type: requestType, message }),
    });
    if (!res.ok) throw new Error('Failed to send request');
    return res.json();
  }

  async getRequests(): Promise<StudentRequest[]> {
    const res = await fetch(`${API_BASE}/communication/requests`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  }

  async updateRequestStatus(requestId: number, status: string, responseNotes?: string): Promise<StudentRequest> {
    const res = await fetch(`${API_BASE}/communication/requests/${requestId}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify({ status, response_notes: responseNotes }),
    });
    if (!res.ok) throw new Error('Failed to update request status');
    return res.json();
  }

  async submitEmotionCheckin(emotion: string, notes?: string, energyLevel: number = 3): Promise<EmotionCheckin> {
    const res = await fetch(`${API_BASE}/communication/emotions`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ emotion, notes, energy_level: energyLevel }),
    });
    if (!res.ok) throw new Error('Failed to record emotion');
    return res.json();
  }

  // Pedagogical Tools
  async simplifyInstruction(originalText: string, readingLevel = 'simple'): Promise<SimplifyResult> {
    const res = await fetch(`${API_BASE}/tools/simplify`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ original_text: originalText, reading_level: readingLevel }),
    });
    if (!res.ok) throw new Error('Simplification failed');
    return res.json();
  }

  async getSchedule(classId?: number): Promise<ScheduleItem[]> {
    const url = classId ? `${API_BASE}/tools/schedule?class_id=${classId}` : `${API_BASE}/tools/schedule`;
    const res = await fetch(url, {
      headers: this.getHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  }

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/tools/stats`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) {
      return {
        total_students: 0,
        total_classes: 0,
        pending_requests: 0,
        unread_messages: 0,
        recent_activities: 0,
      };
    }
    return res.json();
  }
}

export const api = new ApiService();
