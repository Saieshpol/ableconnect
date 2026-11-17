from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Float, DateTime, Date, ForeignKey, Table
)
from sqlalchemy.orm import relationship
from app.core.database import Base

# 1. users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(20), nullable=False)  # 'teacher', 'student', 'guardian', 'admin'
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    guardian_profile = relationship("Guardian", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


# 2. teachers
class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    title = Column(String(50), default="Teacher")
    school_name = Column(String(150), nullable=False, default="Inclusive Academy")
    department = Column(String(100), nullable=True)
    room_number = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    classes = relationship("Classroom", back_populates="teacher", cascade="all, delete-orphan")
    learning_activities = relationship("LearningActivity", back_populates="teacher")
    observations = relationship("TeacherObservation", back_populates="teacher")
    boards = relationship("CommunicationBoard", back_populates="teacher")


# 3. students
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_code = Column(String(50), unique=True, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_color = Column(String(30), default="blue")
    interface_mode = Column(String(30), default="visual_aac")  # 'visual_aac', 'simplified_text', 'audio_assisted'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    profile = relationship("StudentProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("CommunicationPreference", back_populates="student", uselist=False, cascade="all, delete-orphan")
    support_instructions = relationship("SupportInstruction", back_populates="student", cascade="all, delete-orphan")
    enrollments = relationship("ClassStudent", back_populates="student", cascade="all, delete-orphan")
    requests = relationship("StudentRequest", back_populates="student", cascade="all, delete-orphan")
    emotion_checkins = relationship("EmotionCheckin", back_populates="student", cascade="all, delete-orphan")
    progress_records = relationship("StudentProgress", back_populates="student", cascade="all, delete-orphan")
    observations = relationship("TeacherObservation", back_populates="student", cascade="all, delete-orphan")
    custom_boards = relationship("CommunicationBoard", back_populates="student")


# 4. guardians
class Guardian(Base):
    __tablename__ = "guardians"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone_number = Column(String(50), nullable=True)
    relationship_to_student = Column(String(50), nullable=False, default="Parent")
    preferred_contact_method = Column(String(30), default="email")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="guardian_profile")


# 5. classes
class Classroom(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    grade_level = Column(String(50), nullable=False)
    section = Column(String(50), nullable=True)
    room = Column(String(50), nullable=True)
    schedule_summary = Column(String(255), nullable=True)
    color_theme = Column(String(30), default="teal")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="classes")
    students = relationship("ClassStudent", back_populates="classroom", cascade="all, delete-orphan")
    schedules = relationship("ClassroomSchedule", back_populates="classroom", cascade="all, delete-orphan")
    activities = relationship("LearningActivity", back_populates="classroom", cascade="all, delete-orphan")


# 6. class_students
class ClassStudent(Base):
    __tablename__ = "class_students"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="active")

    # Relationships
    classroom = relationship("Classroom", back_populates="students")
    student = relationship("Student", back_populates="enrollments")


# 7. student_profiles
class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferred_name = Column(String(100), nullable=True)
    sensory_profile = Column(Text, nullable=True)
    assistance_level = Column(String(50), default="moderate")  # 'independent', 'minimal', 'moderate', 'intensive'
    alert_preferences = Column(String(100), default="gentle_visual")
    emergency_notes = Column(Text, nullable=True)
    
    # Disability & Certificate Information (Declared by Guardian/Authority, Verified by Admin)
    disability_type = Column(String(100), nullable=True)
    disability_description = Column(Text, nullable=True)
    certificate_filename = Column(String(255), nullable=True)
    certificate_file_path = Column(String(500), nullable=True)
    certificate_mime_type = Column(String(100), nullable=True)
    certificate_file_size = Column(Integer, nullable=True)
    certificate_uploaded_at = Column(DateTime, nullable=True)
    certificate_uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    certificate_verification_status = Column(String(30), default="unsubmitted")  # 'unsubmitted', 'pending', 'verified', 'rejected'
    certificate_verified_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    certificate_verification_notes = Column(Text, nullable=True)
    certificate_verified_at = Column(DateTime, nullable=True)

    updated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="profile")


# 8. communication_preferences
class CommunicationPreference(Base):
    __tablename__ = "communication_preferences"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    verbal_communication = Column(Boolean, default=True)
    written_communication = Column(Boolean, default=True)
    picture_based_communication = Column(Boolean, default=True)
    text_to_speech = Column(Boolean, default=True)
    sign_language = Column(Boolean, default=False)
    gestures = Column(Boolean, default=False)
    custom_methods = Column(Text, nullable=True)
    preferred_symbol_size = Column(String(20), default="large")  # 'standard', 'large', 'extra_large'
    speech_rate = Column(Float, default=1.0)
    high_contrast_mode = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="preferences")


# 9. support_instructions ("How to Communicate With This Student")
class SupportInstruction(Base):
    __tablename__ = "support_instructions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)  # 'communication', 'sensory', 'learning', 'interaction'
    instruction = Column(Text, nullable=False)
    priority = Column(String(20), default="normal")  # 'low', 'normal', 'high', 'essential'
    approved_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="support_instructions")


# 10. messages
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(30), default="text")  # 'text', 'picture_sequence', 'audio_phrase', 'quick_preset'
    attachments = Column(Text, nullable=True)  # JSON-encoded array of symbol keys or media
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])


# 11. communication_boards
class CommunicationBoard(Base):
    __tablename__ = "communication_boards"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="general")  # 'needs', 'emotions', 'classroom', 'activities'
    grid_columns = Column(Integer, default=4)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="custom_boards")
    teacher = relationship("Teacher", back_populates="boards")
    symbols = relationship("CommunicationSymbol", back_populates="board", cascade="all, delete-orphan", order_by="CommunicationSymbol.position_order")


# 12. communication_symbols
class CommunicationSymbol(Base):
    __tablename__ = "communication_symbols"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("communication_boards.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(100), nullable=False)
    icon_name = Column(String(100), nullable=False)  # Lucide icon identifier or SVG name
    speech_text = Column(String(255), nullable=False)  # Spoken phrase
    category = Column(String(50), nullable=False)  # 'pronoun', 'verb', 'need', 'emotion', 'classroom', 'social'
    position_order = Column(Integer, default=0)
    bg_color = Column(String(30), default="bg-blue-50")
    border_color = Column(String(30), default="border-blue-200")

    # Relationships
    board = relationship("CommunicationBoard", back_populates="symbols")


# 13. student_requests (Dignified Student Help Button Queue)
class StudentRequest(Base):
    __tablename__ = "student_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    request_type = Column(String(50), nullable=False)  # 'help', 'break', 'dont_understand', 'washroom', 'uncomfortable'
    message = Column(Text, nullable=True)
    status = Column(String(30), default="sent")  # 'sent', 'seen', 'responded', 'resolved'
    response_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="requests")


# 14. emotion_checkins
class EmotionCheckin(Base):
    __tablename__ = "emotion_checkins"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    emotion = Column(String(50), nullable=False)  # 'happy', 'calm', 'tired', 'confused', 'sad', 'anxious'
    notes = Column(Text, nullable=True)
    energy_level = Column(Integer, default=3)  # 1 (low) to 5 (high)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="emotion_checkins")


# 15. classroom_schedules
class ClassroomSchedule(Base):
    __tablename__ = "classroom_schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    day_of_week = Column(String(20), nullable=False)  # 'Monday', 'Tuesday', etc.
    period_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    start_time = Column(String(10), nullable=False)  # '09:00'
    end_time = Column(String(10), nullable=False)    # '09:45'
    visual_icon = Column(String(50), default="book")
    room = Column(String(50), nullable=True)
    instructions = Column(Text, nullable=True)
    is_current = Column(Boolean, default=False)

    # Relationships
    classroom = relationship("Classroom", back_populates="schedules")


# 16. learning_activities
class LearningActivity(Base):
    __tablename__ = "learning_activities"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    simplified_steps = Column(Text, nullable=True)  # JSON-encoded array of steps
    subject = Column(String(100), nullable=False)
    target_skills = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    classroom = relationship("Classroom", back_populates="activities")
    teacher = relationship("Teacher", back_populates="learning_activities")
    progress_items = relationship("StudentProgress", back_populates="activity")


# 17. student_progress
class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    activity_id = Column(Integer, ForeignKey("learning_activities.id"), nullable=True)
    goal_description = Column(Text, nullable=False)
    baseline = Column(String(100), nullable=True)
    current_status = Column(String(50), default="in_progress")  # 'not_started', 'emerging', 'in_progress', 'achieved'
    progress_percentage = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    recorded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="progress_records")
    activity = relationship("LearningActivity", back_populates="progress_items")


# 18. teacher_observations
class TeacherObservation(Base):
    __tablename__ = "teacher_observations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    observation_date = Column(DateTime, default=datetime.utcnow)
    category = Column(String(50), nullable=False)  # 'learning', 'communication', 'participation', 'challenge', 'effective_strategy'
    content = Column(Text, nullable=False)
    is_private = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="observations")
    teacher = relationship("Teacher", back_populates="observations")


# 19. notifications
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(String(50), default="system")  # 'help_request', 'message', 'schedule', 'system'
    is_read = Column(Boolean, default=False)
    link_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")


# 20. guardian_students (Explicit Guardian-to-Student Authorization Mapping)
class GuardianStudent(Base):
    __tablename__ = "guardian_students"

    id = Column(Integer, primary_key=True, index=True)
    guardian_id = Column(Integer, ForeignKey("guardians.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(50), default="Parent")
    is_authorized = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    guardian = relationship("Guardian", backref="student_links")
    student = relationship("Student", backref="guardian_links")


# 21. certificate_audit_logs (Compliance & Access Audit Logging)
class CertificateAuditLog(Base):
    __tablename__ = "certificate_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_name = Column(String(150), nullable=True)
    user_role = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False)  # 'upload', 'view_details', 'download', 'verify', 'reject'
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")

