from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models import (
    Student, User, StudentProfile, CommunicationPreference,
    SupportInstruction, Classroom, ClassStudent, StudentRequest, EmotionCheckin, Teacher
)
from app.schemas import (
    StudentCardResponse, StudentDetailResponse, CommunicationPreferenceSchema,
    SupportInstructionSchema
)

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=List[StudentCardResponse])
def get_students(claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """
    Returns student roster cards for the teacher dashboard.
    Respects privacy: no raw clinical diagnosis labels shown on cards.
    """
    students = db.query(Student).all()
    results = []

    for s in students:
        user = db.query(User).filter(User.id == s.user_id).first()
        if not user:
            continue

        # Get classes
        class_links = db.query(ClassStudent).filter(ClassStudent.student_id == s.id).all()
        class_names = []
        for link in class_links:
            cls = db.query(Classroom).filter(Classroom.id == link.class_id).first()
            if cls:
                class_names.append(cls.name)

        # Get preferences summary
        pref = db.query(CommunicationPreference).filter(CommunicationPreference.student_id == s.id).first()
        pref_method = "Visual AAC & Symbols"
        if pref:
            if pref.text_to_speech and pref.picture_based_communication:
                pref_method = "Visual AAC + Speech Synthesis"
            elif pref.verbal_communication and not pref.picture_based_communication:
                pref_method = "Verbal & Plain Language"
            elif pref.sign_language:
                pref_method = "Sign Language & Gestures"

        # Get top teacher instruction
        top_inst = db.query(SupportInstruction).filter(
            SupportInstruction.student_id == s.id,
            SupportInstruction.is_active == True
        ).order_by(SupportInstruction.priority.desc()).first()

        # Pending requests count
        pending_count = db.query(StudentRequest).filter(
            StudentRequest.student_id == s.id,
            StudentRequest.status.in_(["sent", "seen"])
        ).count()

        # Latest emotion checkin
        latest_emotion = db.query(EmotionCheckin).filter(
            EmotionCheckin.student_id == s.id
        ).order_by(EmotionCheckin.created_at.desc()).first()

        results.append(
            StudentCardResponse(
                id=s.id,
                user_id=user.id,
                student_code=s.student_code,
                full_name=user.full_name,
                email=user.email,
                avatar_color=s.avatar_color,
                interface_mode=s.interface_mode,
                classes=class_names,
                preferred_communication=pref_method,
                key_instruction=top_inst.instruction if top_inst else "Allow processing time & visual cues.",
                pending_request_count=pending_count,
                latest_emotion=latest_emotion.emotion if latest_emotion else None
            )
        )
    return results

@router.get("/me", response_model=StudentDetailResponse)
def get_student_self(claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """Returns profile for currently logged-in student."""
    user_id = int(claims["sub"])
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found for this account.")
    return _build_student_detail(student, db)

@router.get("/{student_id}", response_model=StudentDetailResponse)
def get_student_detail(student_id: int, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """Returns detailed individual student profile."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return _build_student_detail(student, db)

def _build_student_detail(student: Student, db: Session) -> StudentDetailResponse:
    user = db.query(User).filter(User.id == student.user_id).first()
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student.id).first()
    pref = db.query(CommunicationPreference).filter(CommunicationPreference.student_id == student.id).first()
    instructions = db.query(SupportInstruction).filter(
        SupportInstruction.student_id == student.id,
        SupportInstruction.is_active == True
    ).all()

    class_links = db.query(ClassStudent).filter(ClassStudent.student_id == student.id).all()
    class_names = []
    for link in class_links:
        cls = db.query(Classroom).filter(Classroom.id == link.class_id).first()
        if cls:
            class_names.append(cls.name)

    pref_schema = None
    if pref:
        pref_schema = CommunicationPreferenceSchema(
            verbal_communication=pref.verbal_communication,
            written_communication=pref.written_communication,
            picture_based_communication=pref.picture_based_communication,
            text_to_speech=pref.text_to_speech,
            sign_language=pref.sign_language,
            gestures=pref.gestures,
            custom_methods=pref.custom_methods,
            preferred_symbol_size=pref.preferred_symbol_size,
            speech_rate=pref.speech_rate,
            high_contrast_mode=pref.high_contrast_mode
        )

    inst_schemas = [
        SupportInstructionSchema(
            id=i.id,
            category=i.category,
            instruction=i.instruction,
            priority=i.priority,
            is_active=i.is_active
        )
        for i in instructions
    ]

    return StudentDetailResponse(
        id=student.id,
        user_id=user.id,
        student_code=student.student_code,
        full_name=user.full_name,
        email=user.email,
        avatar_color=student.avatar_color,
        interface_mode=student.interface_mode,
        date_of_birth=student.date_of_birth,
        emergency_contact=student.emergency_contact,
        bio=student.bio,
        sensory_profile=profile.sensory_profile if profile else None,
        assistance_level=profile.assistance_level if profile else "moderate",
        alert_preferences=profile.alert_preferences if profile else "gentle_visual",
        emergency_notes=profile.emergency_notes if profile else None,
        preferences=pref_schema,
        support_instructions=inst_schemas,
        classes=class_names
    )
