from datetime import datetime, date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models import (
    User, Teacher, Student, Guardian, Classroom, ClassStudent,
    StudentProfile, CommunicationPreference, SupportInstruction,
    CommunicationBoard, CommunicationSymbol, StudentRequest,
    EmotionCheckin, ClassroomSchedule, LearningActivity, Message
)

def run_seed():
    print("Dropping and recreating database tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "teacher@ableconnect.org").first():
            print("Database already seeded. Skipping.")
            return

        print("Seeding demo accounts...")
        # 1. Teacher Sarah Jenkins
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

        leo_profile = StudentProfile(
            student_id=leo.id,
            preferred_name="Leo",
            sensory_profile="Sensitive to sudden loud bells; responds well to gentle visual transitions.",
            assistance_level="moderate",
            alert_preferences="gentle_visual",
            emergency_notes="Carries noise-reducing ear defenders in backpack."
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

        maya_profile = StudentProfile(
            student_id=maya.id,
            preferred_name="Maya",
            sensory_profile="Fluorescent light flicker causes visual fatigue. Prefers natural window light.",
            assistance_level="minimal",
            alert_preferences="text_only",
            emergency_notes="Needs seated desk away from hallway door."
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

        # 4. Student Sam Rivera
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
            emergency_notes=None
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

        # 5. Guardian David Chen
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

        # 6. Classrooms
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
        db.add_all([class1, class2])
        db.flush()

        # Enroll students
        enrollments = [
            ClassStudent(class_id=class1.id, student_id=leo.id, status="active"),
            ClassStudent(class_id=class1.id, student_id=maya.id, status="active"),
            ClassStudent(class_id=class1.id, student_id=sam.id, status="active"),
            ClassStudent(class_id=class2.id, student_id=leo.id, status="active"),
            ClassStudent(class_id=class2.id, student_id=maya.id, status="active"),
        ]
        db.add_all(enrollments)

        # 7. Communication Boards & Symbols
        # Board 1: Daily Needs
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

        # Board 2: Emotions & Feelings
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

        # Board 3: Classroom & Sentence Building
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

        # 8. Classroom Timetable
        schedules = [
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Morning Circle & Greeting", subject="Social Check-in", start_time="08:30", end_time="09:00", visual_icon="sun", room="Room 102", instructions="Check in on your emotion board and share your morning goal.", is_current=False),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Interactive Science Lab", subject="Science", start_time="09:00", end_time="10:00", visual_icon="flask-conical", room="Science Corner", instructions="Observing plant seedlings with magnifying glasses.", is_current=True),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Quiet Sensory & Snack Break", subject="Break", start_time="10:00", end_time="10:30", visual_icon="coffee", room="Snack Bar", instructions="Hydration and quiet relaxing time.", is_current=False),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Math Explorations", subject="Mathematics", start_time="10:30", end_time="11:30", visual_icon="calculator", room="Room 102", instructions="Visual block counting and geometric patterns.", is_current=False),
            ClassroomSchedule(class_id=class1.id, day_of_week="Monday", period_name="Creative Art & Expression", subject="Art", start_time="11:30", end_time="12:30", visual_icon="palette", room="Art Nook", instructions="Watercolor painting and tactile textures.", is_current=False),
        ]
        db.add_all(schedules)

        # 9. Sample Help Request
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

        # 10. Sample Emotion Check-in
        leo_checkin = EmotionCheckin(
            student_id=leo.id,
            class_id=class1.id,
            emotion="calm",
            notes="Enjoyed morning music activity.",
            energy_level=3,
            created_at=datetime.utcnow()
        )
        db.add(leo_checkin)

        # 11. Sample Learning Activity
        activity = LearningActivity(
            class_id=class1.id,
            teacher_id=teacher.id,
            title="Plant Seedling Observation Journal",
            description="Look closely at your seedling. Record leaf count and draw the root structure.",
            simplified_steps='[{"step_number": 1, "text": "Pick up your seedling cup.", "icon": "package"}, {"step_number": 2, "text": "Count the green leaves.", "icon": "eye"}, {"step_number": 3, "text": "Draw the shape of the leaf in your journal.", "icon": "edit-3"}]',
            subject="Science",
            target_skills="Observation, Fine Motor, Counting"
        )
        db.add(activity)

        # 12. Sample Message
        msg = Message(
            sender_id=teacher_user.id,
            recipient_id=leo_user.id,
            content="Great job participating in today's plant observation lesson, Leo! Your drawing was wonderful.",
            message_type="text",
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(msg)

        db.commit()
        print("Demo data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
