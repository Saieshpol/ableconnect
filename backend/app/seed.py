import os
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.core.config import settings
from app.models import (
    User, Teacher, Student, Guardian, Classroom, ClassStudent,
    StudentProfile, CommunicationPreference, SupportInstruction,
    CommunicationBoard, CommunicationSymbol, StudentRequest,
    EmotionCheckin, ClassroomSchedule, LearningActivity, Message,
    GuardianStudent, CertificateAuditLog
)

def create_sample_pdf(filepath: str, title: str, student_name: str, clinician: str, content: str):
    """Creates a valid, lightweight PDF file for realistic certificate downloading and viewing."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pdf_content = (
        f"%PDF-1.4\n"
        f"1 0 obj << /Title ({title}) /Author ({clinician}) >> endobj\n"
        f"2 0 obj << /Type /Catalog /Pages 3 0 R >> endobj\n"
        f"3 0 obj << /Type /Pages /Kids [4 0 R] /Count 1 >> endobj\n"
        f"4 0 obj << /Type /Page /Parent 3 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >> endobj\n"
        f"5 0 obj << /Length 200 >> stream\n"
        f"BT /F1 14 Tf 50 720 Td ({title}) Tj\n"
        f"/F1 10 Tf 0 -25 Td (Student: {student_name}) Tj\n"
        f"0 -15 Td (Evaluating Authority: {clinician}) Tj\n"
        f"0 -25 Td ({content}) Tj ET\n"
        f"endstream endobj\n"
        f"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000136 00000 n \n0000000201 00000 n \n0000000305 00000 n \n"
        f"trailer << /Size 6 /Root 2 0 R >>\nstartxref\n550\n%%EOF\n"
    )
    with open(filepath, "wb") as f:
        f.write(pdf_content.encode("latin-1"))

def run_seed():
    if settings.ENVIRONMENT.lower() != "development" or not settings.SEED_DEMO_DATA:
        raise RuntimeError("Demo seeding is permitted only when ENVIRONMENT=development and SEED_DEMO_DATA=true.")
    print("Ensuring local demo database tables exist...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "teacher@ableconnect.org").first():
            print("Database already seeded. Skipping.")
            return

        print("Seeding demo accounts and authorized certificates...")

        # 0. Administrator Dr. Eleanor Vance (Can verify certificates)
        admin_user = User(
            email="admin@ableconnect.org",
            hashed_password=hash_password("admin123"),
            full_name="Dr. Eleanor Vance, Administrator",
            role="admin",
            avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(admin_user)
        db.flush()

        # 1. Teacher Sarah Jenkins (Lead Special Ed Teacher - Room 102)
        teacher_user = User(
            email="teacher@ableconnect.org",
            hashed_password=hash_password("teacher123"),
            full_name="Sarah Jenkins, M.Ed.",
            role="teacher",
            avatar_url="https://images.unsplash.com/photo-1544717305-2782549b5136?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(teacher_user)
        db.flush()

        teacher = Teacher(
            user_id=teacher_user.id,
            title="Lead Inclusive Education Specialist",
            school_name="Oakridge Elementary Inclusive Academy",
            department="Specialized & Inclusive Learning",
            room_number="Room 102"
        )
        db.add(teacher)
        db.flush()

        # 1b. Second Teacher Mr. Robert Adams (Room 204 - For Class-Boundary Authorization Testing)
        teacher_user2 = User(
            email="adams@ableconnect.org",
            hashed_password=hash_password("teacher123"),
            full_name="Robert Adams, B.Ed.",
            role="teacher",
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(teacher_user2)
        db.flush()

        teacher2 = Teacher(
            user_id=teacher_user2.id,
            title="Senior Elementary Educator",
            school_name="Oakridge Elementary Inclusive Academy",
            department="Upper Primary",
            room_number="Room 204"
        )
        db.add(teacher2)
        db.flush()

        # Storage directory for certificates
        storage_dir = settings.CERTIFICATES_STORAGE_DIR
        os.makedirs(storage_dir, exist_ok=True)

        # 2. Student Leo Vance (AAC & Visual Communicator)
        leo_user = User(
            email="leo@ableconnect.org",
            hashed_password=hash_password("student123"),
            full_name="Leo Vance",
            role="student",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(leo_user)
        db.flush()

        leo = Student(
            user_id=leo_user.id,
            student_code="STU-0101",
            date_of_birth=date(2016, 5, 14),
            emergency_contact="+1 (555) 234-5678 (David Chen - Parent)",
            bio="Loves hands-on science, building blocks, and illustrated nature stories.",
            avatar_color="teal",
            interface_mode="visual_aac"
        )
        db.add(leo)
        db.flush()

        # Create sample certificate file for Leo
        leo_cert_path = os.path.join(storage_dir, "cert_stu_1_leo_speech_assessment.pdf")
        create_sample_pdf(
            filepath=leo_cert_path,
            title="Comprehensive Speech & Language Pathology Assessment",
            student_name="Leo Vance (DOB: 2016-05-14)",
            clinician="Metro Children's Developmental Health Center",
            content="Diagnosis: Expressive Language Delay. Recommends AAC visual communication boards and additional processing time."
        )

        leo_profile = StudentProfile(
            student_id=leo.id,
            preferred_name="Leo",
            sensory_profile="Sensitive to sudden loud bells; responds well to gentle visual transitions.",
            assistance_level="moderate",
            alert_preferences="gentle_visual",
            emergency_notes="Carries noise-reducing ear defenders in backpack.",
            # Disability & Certificate Information
            disability_type="Speech & Communication Impairment",
            disability_description="Expressive language delay with strong receptive comprehension. Certified by Metro Children's Developmental Health Center.",
            certificate_filename="leo_vance_speech_evaluation_report.pdf",
            certificate_file_path=leo_cert_path,
            certificate_mime_type="application/pdf",
            certificate_file_size=os.path.getsize(leo_cert_path),
            certificate_uploaded_at=datetime(2026, 9, 2, 10, 30),
            certificate_uploaded_by_user_id=None,
            certificate_verification_status="verified",
            certificate_verified_by_user_id=admin_user.id,
            certificate_verification_notes="Official pediatric speech pathology evaluation verified by school administration.",
            certificate_verified_at=datetime(2026, 9, 5, 14, 0)
        )
        db.add(leo_profile)

        leo_pref = CommunicationPreference(
            student_id=leo.id,
            verbal_communication=False,
            written_communication=True,
            picture_based_communication=True,
            text_to_speech=True,
            sign_language=False,
            gestures=True,
            custom_methods="Uses 2-3 symbol picture sequencing with text-to-speech feedback.",
            preferred_symbol_size="large",
            speech_rate=0.9,
            high_contrast_mode=False
        )
        db.add(leo_pref)

        leo_inst1 = SupportInstruction(
            student_id=leo.id,
            category="communication",
            instruction="Allow 8-10 seconds processing time before repeating a question.",
            priority="essential",
            is_active=True
        )
        leo_inst2 = SupportInstruction(
            student_id=leo.id,
            category="interaction",
            instruction="Accept responses made via picture card selections and audio synthesis.",
            priority="high",
            is_active=True
        )
        leo_inst3 = SupportInstruction(
            student_id=leo.id,
            category="sensory",
            instruction="Provide a 2-minute visual cue before transition to lunch or gym.",
            priority="normal",
            is_active=True
        )
        db.add_all([leo_inst1, leo_inst2, leo_inst3])

        # 3. Student Maya Patel (Sensory-sensitive, step-by-step)
        maya_user = User(
            email="maya@ableconnect.org",
            hashed_password=hash_password("student123"),
            full_name="Maya Patel",
            role="student",
            avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(maya_user)
        db.flush()

        maya = Student(
            user_id=maya_user.id,
            student_code="STU-0102",
            date_of_birth=date(2015, 11, 20),
            emergency_contact="+1 (555) 876-5432",
            bio="Enjoys reading fiction, drawing, and quiet puzzle-solving.",
            avatar_color="purple",
            interface_mode="simplified_text"
        )
        db.add(maya)
        db.flush()

        # Create sample certificate file for Maya (Pending status)
        maya_cert_path = os.path.join(storage_dir, "cert_stu_2_maya_sensory_report.pdf")
        create_sample_pdf(
            filepath=maya_cert_path,
            title="Sensory Processing & Visual Ergonomics Report",
            student_name="Maya Patel (DOB: 2015-11-20)",
            clinician="Pediatric Occupational Therapy Associates",
            content="Diagnosis: Sensory Sensitivity (Visual/Lighting). Recommends indirect natural lighting and step-by-step written task cards."
        )

        maya_profile = StudentProfile(
            student_id=maya.id,
            preferred_name="Maya",
            sensory_profile="Fluorescent light flicker causes visual fatigue. Prefers natural window light.",
            assistance_level="minimal",
            alert_preferences="text_only",
            emergency_notes="Needs seated desk away from hallway door.",
            disability_type="Sensory Processing Sensitivity & Visual Fatigue",
            disability_description="Visual light sensitivity to fluorescent lighting; benefits from natural window light and step-by-step task breakdown.",
            certificate_filename="maya_patel_sensory_evaluation.pdf",
            certificate_file_path=maya_cert_path,
            certificate_mime_type="application/pdf",
            certificate_file_size=os.path.getsize(maya_cert_path),
            certificate_uploaded_at=datetime(2026, 11, 10, 9, 15),
            certificate_verification_status="pending",
            certificate_verified_by_user_id=None,
            certificate_verification_notes=None,
            certificate_verified_at=None
        )
        db.add(maya_profile)

        maya_pref = CommunicationPreference(
            student_id=maya.id,
            verbal_communication=True,
            written_communication=True,
            picture_based_communication=True,
            text_to_speech=False,
            sign_language=False,
            gestures=False,
            preferred_symbol_size="standard",
            speech_rate=1.0,
            high_contrast_mode=True
        )
        db.add(maya_pref)

        maya_inst1 = SupportInstruction(
            student_id=maya.id,
            category="learning",
            instruction="Break compound assignments into numbered steps with single-task focus.",
            priority="essential",
            is_active=True
        )
        maya_inst2 = SupportInstruction(
            student_id=maya.id,
            category="sensory",
            instruction="Allow quiet sensory breaks in the reading nook when feeling overwhelmed.",
            priority="high",
            is_active=True
        )
        db.add_all([maya_inst1, maya_inst2])

        # 4. Student Sam Rivera (No certificate uploaded yet: "unsubmitted" state)
        sam_user = User(
            email="sam@ableconnect.org",
            hashed_password=hash_password("student123"),
            full_name="Sam Rivera",
            role="student",
            avatar_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(sam_user)
        db.flush()

        sam = Student(
            user_id=sam_user.id,
            student_code="STU-0103",
            date_of_birth=date(2016, 2, 8),
            emergency_contact="+1 (555) 345-6789",
            bio="Enthusiastic participant in group discussions; benefits from structured checklists.",
            avatar_color="amber",
            interface_mode="audio_assisted"
        )
        db.add(sam)
        db.flush()

        sam_profile = StudentProfile(
            student_id=sam.id,
            preferred_name="Sam",
            sensory_profile="High energy; benefits from kinesthetic movement breaks.",
            assistance_level="minimal",
            alert_preferences="gentle_visual",
            emergency_notes=None,
            disability_type="Attention & Executive Functioning Focus",
            disability_description="Benefits from short visual checklists and movement breaks every 20 minutes.",
            certificate_filename=None,
            certificate_file_path=None,
            certificate_mime_type=None,
            certificate_file_size=None,
            certificate_uploaded_at=None,
            certificate_verification_status="unsubmitted",
            certificate_verified_by_user_id=None,
            certificate_verification_notes=None,
            certificate_verified_at=None
        )
        db.add(sam_profile)

        sam_pref = CommunicationPreference(
            student_id=sam.id,
            verbal_communication=True,
            written_communication=True,
            picture_based_communication=True,
            text_to_speech=True,
            sign_language=False,
            gestures=True,
            preferred_symbol_size="standard",
            speech_rate=1.1,
            high_contrast_mode=False
        )
        db.add(sam_pref)

        sam_inst1 = SupportInstruction(
            student_id=sam.id,
            category="learning",
            instruction="Provide written checklist of 3 tasks at a time. Celebrate each completion.",
            priority="high",
            is_active=True
        )
        db.add(sam_inst1)

        # 5. Student Chloe Kim (Enrolled in Mr. Adams's Room 204 ONLY - NOT in Sarah's classes)
        chloe_user = User(
            email="chloe@ableconnect.org",
            hashed_password=hash_password("student123"),
            full_name="Chloe Kim",
            role="student",
            avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(chloe_user)
        db.flush()

        chloe = Student(
            user_id=chloe_user.id,
            student_code="STU-0201",
            date_of_birth=date(2015, 8, 12),
            emergency_contact="+1 (555) 456-7890",
            bio="Loves mathematics, drawing, and interactive group storytelling.",
            avatar_color="teal",
            interface_mode="visual_aac"
        )
        db.add(chloe)
        db.flush()

        chloe_cert_path = os.path.join(storage_dir, "cert_stu_4_chloe_audiology.pdf")
        create_sample_pdf(
            filepath=chloe_cert_path,
            title="Pediatric Audiological Assessment",
            student_name="Chloe Kim (DOB: 2015-08-12)",
            clinician="State Children's Hearing Clinic",
            content="Diagnosis: Bilateral Moderate Hearing Loss. Benefits from assistive FM listening system and preferential front seating."
        )

        chloe_profile = StudentProfile(
            student_id=chloe.id,
            preferred_name="Chloe",
            sensory_profile="Moderate bilateral hearing loss. Benefits from clear visual cues.",
            assistance_level="moderate",
            alert_preferences="gentle_visual",
            emergency_notes=None,
            disability_type="Hearing Impairment",
            disability_description="Bilateral moderate hearing loss. Uses classroom FM system and visual prompts.",
            certificate_filename="chloe_kim_audiology_report.pdf",
            certificate_file_path=chloe_cert_path,
            certificate_mime_type="application/pdf",
            certificate_file_size=os.path.getsize(chloe_cert_path),
            certificate_uploaded_at=datetime(2026, 10, 15, 11, 0),
            certificate_verification_status="verified",
            certificate_verified_by_user_id=admin_user.id,
            certificate_verification_notes="Audiological report verified by administration.",
            certificate_verified_at=datetime(2026, 10, 18, 9, 30)
        )
        db.add(chloe_profile)

        # 6. Guardian David Chen (Authorized for Leo Vance)
        guardian_user = User(
            email="guardian@ableconnect.org",
            hashed_password=hash_password("guardian123"),
            full_name="David Chen",
            role="guardian",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            is_active=True
        )
        db.add(guardian_user)
        db.flush()

        guardian = Guardian(
            user_id=guardian_user.id,
            phone_number="+1 (555) 234-5678",
            relationship_to_student="Parent",
            preferred_contact_method="email"
        )
        db.add(guardian)
        db.flush()

        # Link Guardian David Chen to Leo Vance
        guardian_link = GuardianStudent(
            guardian_id=guardian.id,
            student_id=leo.id,
            relationship_type="Parent",
            is_authorized=True,
            created_at=datetime.utcnow()
        )
        db.add(guardian_link)

        # 7. Classrooms
        class1 = Classroom(
            teacher_id=teacher.id,
            name="Room 102 - Inclusive Grade 3",
            grade_level="Grade 3",
            section="Section A",
            room="Room 102",
            schedule_summary="Mon-Fri 08:30 - 14:45",
            color_theme="teal",
            is_active=True
        )
        class2 = Classroom(
            teacher_id=teacher.id,
            name="Discovery STEM & Creative Arts",
            grade_level="Mixed",
            section="Section B",
            room="Lab 3",
            schedule_summary="Tue & Thu 10:00 - 11:30",
            color_theme="indigo",
            is_active=True
        )
        class3 = Classroom(
            teacher_id=teacher2.id,
            name="Room 204 - Grade 4 Exploration",
            grade_level="Grade 4",
            section="Section C",
            room="Room 204",
            schedule_summary="Mon-Fri 08:30 - 14:30",
            color_theme="purple",
            is_active=True
        )
        db.add_all([class1, class2, class3])
        db.flush()

        # Enrollments
        # Leo, Maya, Sam are in Teacher Sarah Jenkins's classes (class1 and/or class2)
        # Chloe is ONLY in Teacher Robert Adams's class (class3)
        enrollments = [
            ClassStudent(class_id=class1.id, student_id=leo.id, status="active"),
            ClassStudent(class_id=class1.id, student_id=maya.id, status="active"),
            ClassStudent(class_id=class1.id, student_id=sam.id, status="active"),
            ClassStudent(class_id=class2.id, student_id=leo.id, status="active"),
            ClassStudent(class_id=class2.id, student_id=maya.id, status="active"),
            ClassStudent(class_id=class3.id, student_id=chloe.id, status="active"),
        ]
        db.add_all(enrollments)

        # 8. Communication Boards & Symbols
        board_needs = CommunicationBoard(
            student_id=None,
            teacher_id=teacher.id,
            title="Core Daily Needs",
            description="Essential daily assistance, comfort, and physiological needs",
            category="needs",
            grid_columns=3,
            is_default=True,
            is_public=True
        )
        db.add(board_needs)
        db.flush()

        needs_symbols = [
            CommunicationSymbol(board_id=board_needs.id, label="Help", icon_name="help-circle", speech_text="I need help", category="need", position_order=1, bg_color="bg-amber-50", border_color="border-amber-300"),
            CommunicationSymbol(board_id=board_needs.id, label="Break", icon_name="coffee", speech_text="I need a break", category="need", position_order=2, bg_color="bg-teal-50", border_color="border-teal-300"),
            CommunicationSymbol(board_id=board_needs.id, label="Washroom", icon_name="bath", speech_text="I need to use the washroom", category="need", position_order=3, bg_color="bg-blue-50", border_color="border-blue-300"),
            CommunicationSymbol(board_id=board_needs.id, label="Water", icon_name="droplet", speech_text="I would like some water", category="need", position_order=4, bg_color="bg-cyan-50", border_color="border-cyan-300"),
            CommunicationSymbol(board_id=board_needs.id, label="Quiet Space", icon_name="volume-x", speech_text="I need a quiet space", category="need", position_order=5, bg_color="bg-indigo-50", border_color="border-indigo-300"),
            CommunicationSymbol(board_id=board_needs.id, label="More Time", icon_name="clock", speech_text="I need more time, please", category="need", position_order=6, bg_color="bg-emerald-50", border_color="border-emerald-300"),
        ]
        db.add_all(needs_symbols)

        board_emotions = CommunicationBoard(
            student_id=None,
            teacher_id=teacher.id,
            title="Emotions & Feelings",
            description="Express emotional states and feelings comfortably",
            category="emotions",
            grid_columns=3,
            is_default=False,
            is_public=True
        )
        db.add(board_emotions)
        db.flush()

        emotion_symbols = [
            CommunicationSymbol(board_id=board_emotions.id, label="Happy", icon_name="smile", speech_text="I feel happy", category="emotion", position_order=1, bg_color="bg-emerald-50", border_color="border-emerald-300"),
            CommunicationSymbol(board_id=board_emotions.id, label="Calm", icon_name="heart", speech_text="I feel calm", category="emotion", position_order=2, bg_color="bg-teal-50", border_color="border-teal-300"),
            CommunicationSymbol(board_id=board_emotions.id, label="Confused", icon_name="help-circle", speech_text="I feel confused", category="emotion", position_order=3, bg_color="bg-amber-50", border_color="border-amber-300"),
            CommunicationSymbol(board_id=board_emotions.id, label="Tired", icon_name="moon", speech_text="I am feeling tired", category="emotion", position_order=4, bg_color="bg-slate-50", border_color="border-slate-300"),
            CommunicationSymbol(board_id=board_emotions.id, label="Sad", icon_name="frown", speech_text="I feel sad", category="emotion", position_order=5, bg_color="bg-blue-50", border_color="border-blue-300"),
            CommunicationSymbol(board_id=board_emotions.id, label="Uncomfortable", icon_name="alert-circle", speech_text="I feel uncomfortable", category="emotion", position_order=6, bg_color="bg-rose-50", border_color="border-rose-300"),
        ]
        db.add_all(emotion_symbols)

        board_sentence = CommunicationBoard(
            student_id=None,
            teacher_id=teacher.id,
            title="Classroom & Sentence Building",
            description="Grammar tokens and classroom interaction cards",
            category="classroom",
            grid_columns=4,
            is_default=False,
            is_public=True
        )
        db.add(board_sentence)
        db.flush()

        sentence_symbols = [
            CommunicationSymbol(board_id=board_sentence.id, label="I", icon_name="user", speech_text="I", category="pronoun", position_order=1, bg_color="bg-blue-50", border_color="border-blue-300"),
            CommunicationSymbol(board_id=board_sentence.id, label="Need", icon_name="hand", speech_text="need", category="verb", position_order=2, bg_color="bg-yellow-50", border_color="border-yellow-300"),
            CommunicationSymbol(board_id=board_sentence.id, label="Help", icon_name="life-buoy", speech_text="help", category="noun", position_order=3, bg_color="bg-rose-50", border_color="border-rose-300"),
            CommunicationSymbol(board_id=board_sentence.id, label="Break", icon_name="coffee", speech_text="a break", category="noun", position_order=4, bg_color="bg-teal-50", border_color="border-teal-300"),
            CommunicationSymbol(board_id=board_sentence.id, label="Yes", icon_name="check", speech_text="Yes", category="social", position_order=5, bg_color="bg-green-50", border_color="border-green-300"),
            CommunicationSymbol(board_id=board_sentence.id, label="No", icon_name="x", speech_text="No", category="social", position_order=6, bg_color="bg-red-50", border_color="border-red-300"),
            CommunicationSymbol(board_id=board_sentence.id, label="Finished", icon_name="check-circle", speech_text="I finished my work", category="social", position_order=7, bg_color="bg-indigo-50", border_color="border-indigo-300"),
            CommunicationSymbol(board_id=board_sentence.id, label="Question", icon_name="help-circle", speech_text="I have a question", category="social", position_order=8, bg_color="bg-purple-50", border_color="border-purple-300"),
        ]
        db.add_all(sentence_symbols)

        # 9. Classroom Timetable
        schedules = [
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Morning Circle & Greeting", subject="Social Check-in", start_time="08:30", end_time="09:00", visual_icon="sun", room="Room 102", instructions="Check in on your emotion board and share your morning goal.", is_current=False),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Interactive Science Lab", subject="Science", start_time="09:00", end_time="10:00", visual_icon="flask-conical", room="Science Corner", instructions="Observing plant seedlings with magnifying glasses.", is_current=True),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Quiet Sensory & Snack Break", subject="Break", start_time="10:00", end_time="10:30", visual_icon="coffee", room="Snack Bar", instructions="Hydration and quiet relaxing time.", is_current=False),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Math Explorations", subject="Mathematics", start_time="10:30", end_time="11:30", visual_icon="calculator", room="Room 102", instructions="Visual block counting and geometric patterns.", is_current=False),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Creative Art & Expression", subject="Art", start_time="11:30", end_time="12:30", visual_icon="palette", room="Art Nook", instructions="Watercolor painting and tactile textures.", is_current=False),
        ]
        db.add_all(schedules)

        # 10. Sample Help Request
        sample_request = StudentRequest(
            student_id=leo.id,
            teacher_id=teacher.id,
            class_id=class1.id,
            request_type="break",
            message="Leo requested a quiet break in the sensory reading corner.",
            status="sent",
            created_at=datetime.utcnow()
        )
        db.add(sample_request)

        # 11. Initial Audit Log
        audit_log = CertificateAuditLog(
            student_id=leo.id,
            user_id=admin_user.id,
            user_name=admin_user.full_name,
            user_role="admin",
            action="verify",
            details="Initial setup: Official pediatric evaluation report verified by administration.",
            ip_address="127.0.0.1",
            created_at=datetime(2026, 9, 5, 14, 0)
        )
        db.add(audit_log)

        db.commit()
        print("Demo data and certificates seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
