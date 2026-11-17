export type UserRole = 'teacher' | 'student' | 'guardian' | 'admin';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  avatar_url?: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface StudentCard {
  id: number;
  user_id: number;
  student_code: string;
  full_name: string;
  email: string;
  avatar_color: string;
  interface_mode: string;
  classes: string[];
  preferred_communication: string;
  key_instruction?: string;
  pending_request_count: number;
  latest_emotion?: string;
}

export interface CommunicationPreference {
  verbal_communication: boolean;
  written_communication: boolean;
  picture_based_communication: boolean;
  text_to_speech: boolean;
  sign_language: boolean;
  gestures: boolean;
  custom_methods?: string;
  preferred_symbol_size: string;
  speech_rate: number;
  high_contrast_mode: boolean;
}

export interface SupportInstruction {
  id: number;
  category: string;
  instruction: string;
  priority: string;
  is_active: boolean;
}

export interface DisabilityCertificateInfo {
  disability_type?: string;
  disability_description?: string;
  has_certificate: boolean;
  certificate_filename?: string;
  certificate_mime_type?: string;
  certificate_file_size?: number;
  certificate_uploaded_at?: string;
  certificate_verification_status: 'unsubmitted' | 'pending' | 'verified' | 'rejected';
  certificate_verification_notes?: string;
  certificate_verified_at?: string;
  can_access_certificate: boolean;
}

export interface StudentDetail {
  id: number;
  user_id: number;
  student_code: string;
  full_name: string;
  email: string;
  avatar_color: string;
  interface_mode: string;
  date_of_birth?: string;
  emergency_contact?: string;
  bio?: string;
  sensory_profile?: string;
  assistance_level: string;
  alert_preferences: string;
  emergency_notes?: string;
  preferences?: CommunicationPreference;
  support_instructions: SupportInstruction[];
  classes: string[];
  disability_info?: DisabilityCertificateInfo;
}

export interface CommunicationSymbol {
  id: number;
  label: string;
  icon_name: string;
  speech_text: string;
  category: string;
  position_order: number;
  bg_color: string;
  border_color: string;
}

export interface CommunicationBoard {
  id: number;
  title: string;
  description?: string;
  category: string;
  grid_columns: number;
  is_default: boolean;
  symbols: CommunicationSymbol[];
}

export interface StudentRequest {
  id: number;
  student_id: number;
  student_name?: string;
  teacher_id?: number;
  class_id?: number;
  request_type: string;
  message?: string;
  status: 'sent' | 'seen' | 'responded' | 'resolved';
  response_notes?: string;
  created_at: string;
  responded_at?: string;
}

export interface EmotionCheckin {
  id: number;
  student_id: number;
  emotion: string;
  notes?: string;
  energy_level: number;
  created_at: string;
}

export interface Classroom {
  id: number;
  name: string;
  grade_level: string;
  section?: string;
  room?: string;
  schedule_summary?: string;
  color_theme: string;
  student_count: number;
  is_active: boolean;
  created_at: string;
}

export interface ScheduleItem {
  id: number;
  period_name: string;
  subject: string;
  start_time: string;
  end_time: string;
  visual_icon: string;
  room?: string;
  instructions?: string;
  is_current: boolean;
}

export interface SimplifiedStep {
  step_number: number;
  text: string;
  icon: string;
}

export interface SimplifyResult {
  original_text: string;
  steps: SimplifiedStep[];
  simplified_summary: string;
  audio_ready_text: string;
  method_used: string;
}

export interface DashboardStats {
  total_students: number;
  total_classes: number;
  pending_requests: number;
  unread_messages: number;
  recent_activities: number;
}
