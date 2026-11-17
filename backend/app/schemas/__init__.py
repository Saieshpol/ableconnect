from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict

# Auth & User schemas
class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class DemoSwitchRequest(BaseModel):
    target_role: str  # 'teacher', 'student', 'guardian'
    student_id: Optional[int] = None

# Communication Board & AAC schemas
class SymbolSchema(BaseModel):
    id: int
    label: str
    icon_name: str
    speech_text: str
    category: str
    position_order: int
    bg_color: str
    border_color: str

    model_config = ConfigDict(from_attributes=True)

class BoardSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: str
    grid_columns: int
    is_default: bool
    symbols: List[SymbolSchema] = []

    model_config = ConfigDict(from_attributes=True)

class SentenceSynthesizeRequest(BaseModel):
    symbols: List[str]

class SentenceSynthesizeResponse(BaseModel):
    sentence: str
    spoken_text: str
    category: str

# Student Request (Help Button)
class StudentRequestCreate(BaseModel):
    request_type: str  # 'help', 'break', 'dont_understand', 'washroom', 'uncomfortable'
    message: Optional[str] = None
    class_id: Optional[int] = None

class StudentRequestUpdate(BaseModel):
    status: str  # 'sent', 'seen', 'responded', 'resolved'
    response_notes: Optional[str] = None

class StudentRequestResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    request_type: str
    message: Optional[str] = None
    status: str
    response_notes: Optional[str] = None
    created_at: datetime
    responded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Emotion Check-in
class EmotionCheckinCreate(BaseModel):
    emotion: str
    notes: Optional[str] = None
    energy_level: int = 3
    class_id: Optional[int] = None

class EmotionCheckinResponse(BaseModel):
    id: int
    student_id: int
    emotion: str
    notes: Optional[str] = None
    energy_level: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Support Instructions ("How to communicate with this student")
class SupportInstructionSchema(BaseModel):
    id: int
    category: str
    instruction: str
    priority: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# Communication Preferences
class CommunicationPreferenceSchema(BaseModel):
    verbal_communication: bool
    written_communication: bool
    picture_based_communication: bool
    text_to_speech: bool
    sign_language: bool
    gestures: bool
    custom_methods: Optional[str] = None
    preferred_symbol_size: str
    speech_rate: float
    high_contrast_mode: bool

    model_config = ConfigDict(from_attributes=True)

# Student Profile & Detail
class StudentCardResponse(BaseModel):
    id: int
    user_id: int
    student_code: str
    full_name: str
    email: str
    avatar_color: str
    interface_mode: str
    classes: List[str] = []
    preferred_communication: str
    key_instruction: Optional[str] = None
    pending_request_count: int = 0
    latest_emotion: Optional[str] = None

class StudentDetailResponse(BaseModel):
    id: int
    user_id: int
    student_code: str
    full_name: str
    email: str
    avatar_color: str
    interface_mode: str
    date_of_birth: Optional[date] = None
    emergency_contact: Optional[str] = None
    bio: Optional[str] = None
    sensory_profile: Optional[str] = None
    assistance_level: str
    alert_preferences: str
    emergency_notes: Optional[str] = None
    preferences: Optional[CommunicationPreferenceSchema] = None
    support_instructions: List[SupportInstructionSchema] = []
    classes: List[str] = []

# Class schemas
class ClassroomCreate(BaseModel):
    name: str
    grade_level: str
    section: Optional[str] = None
    room: Optional[str] = None
    color_theme: Optional[str] = "teal"

class ClassroomResponse(BaseModel):
    id: int
    name: str
    grade_level: str
    section: Optional[str] = None
    room: Optional[str] = None
    schedule_summary: Optional[str] = None
    color_theme: str
    student_count: int = 0
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Instruction Simplifier
class SimplifyRequest(BaseModel):
    original_text: str
    reading_level: Optional[str] = "simple"
    target_steps: Optional[int] = None
    add_visual_cues: bool = True

class SimplifiedStep(BaseModel):
    step_number: int
    text: str
    icon: str

class SimplifyResponse(BaseModel):
    original_text: str
    steps: List[SimplifiedStep]
    simplified_summary: str
    audio_ready_text: str
    method_used: str  # 'rule_based' or 'ai_provider'

# Schedule schema
class ScheduleItemResponse(BaseModel):
    id: int
    period_name: str
    subject: str
    start_time: str
    end_time: str
    visual_icon: str
    room: Optional[str] = None
    instructions: Optional[str] = None
    is_current: bool = False

    model_config = ConfigDict(from_attributes=True)

# Message schema
class MessageCreate(BaseModel):
    recipient_id: int
    content: str
    message_type: Optional[str] = "text"
    attachments: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    recipient_id: int
    recipient_name: str
    content: str
    message_type: str
    attachments: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
