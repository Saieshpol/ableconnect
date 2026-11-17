from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models import (
    ClassroomSchedule, Classroom, Student, StudentRequest, Message, LearningActivity,
    ClassStudent, Teacher, Guardian, GuardianStudent
)
from app.schemas import (
    SimplifyRequest, SimplifyResponse, SimplifiedStep, ScheduleItemResponse
)
from app.services.simplifier import InstructionSimplifier

router = APIRouter(prefix="/tools", tags=["Pedagogical Tools"])

@router.post("/simplify", response_model=SimplifyResponse)
async def simplify_instruction(payload: SimplifyRequest, claims: dict = Depends(get_current_user_claims)):
    """
    Simplifies compound classroom instructions into step-by-step
    accessible items with visual icon cues and speech-ready text.
    """
    if claims.get("role") not in {"teacher", "admin"}:
        raise HTTPException(status_code=403, detail="Only teachers and administrators can simplify classroom instructions.")
    res = await InstructionSimplifier.simplify(payload.original_text, payload.reading_level or "simple")
    
    steps = [
        SimplifiedStep(
            step_number=s["step_number"],
            text=s["text"],
            icon=s["icon"]
        )
        for s in res["steps"]
    ]

    return SimplifyResponse(
        original_text=res["original_text"],
        steps=steps,
        simplified_summary=res["simplified_summary"],
        audio_ready_text=res["audio_ready_text"],
        method_used=res["method_used"]
    )

@router.get("/schedule", response_model=List[ScheduleItemResponse])
def get_schedule(class_id: Optional[int] = None, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """Returns visual classroom timetable entries."""
    query = db.query(ClassroomSchedule)
    user_id = int(claims["sub"])
    role = claims["role"]
    student_id = None
    if role == "admin":
        allowed_class_ids = [row[0] for row in db.query(Classroom.id).filter(Classroom.is_active == True).all()]
    elif role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        allowed_class_ids = [row[0] for row in db.query(Classroom.id).filter(Classroom.teacher_id == teacher.id, Classroom.is_active == True).all()] if teacher else []
    elif role == "student":
        student = db.query(Student).filter(Student.user_id == user_id).first()
        student_id = student.id if student else None
        allowed_class_ids = [link.class_id for link in db.query(ClassStudent).filter(ClassStudent.student_id == student_id, ClassStudent.status == "active").all()] if student_id else []
    elif role == "guardian":
        guardian = db.query(Guardian).filter(Guardian.user_id == user_id).first()
        student_ids = [row[0] for row in db.query(GuardianStudent.student_id).filter(
            GuardianStudent.guardian_id == guardian.id if guardian else False,
            GuardianStudent.is_authorized == True,
        ).all()] if guardian else []
        allowed_class_ids = [row[0] for row in db.query(ClassStudent.class_id).join(GuardianStudent, GuardianStudent.student_id == ClassStudent.student_id).filter(
            GuardianStudent.guardian_id == guardian.id if guardian else False,
            GuardianStudent.is_authorized == True, ClassStudent.status == "active",
        ).distinct().all()] if guardian else []
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view schedules.")
    query = query.filter(ClassroomSchedule.class_id.in_(allowed_class_ids))
    if class_id is not None:
        if class_id not in allowed_class_ids:
            raise HTTPException(status_code=403, detail="Not authorized to view this class schedule.")
        query = query.filter(ClassroomSchedule.class_id == class_id)
    if student_id is not None:
        query = query.filter((ClassroomSchedule.student_id.is_(None)) | (ClassroomSchedule.student_id == student_id))
    elif role == "guardian":
        query = query.filter((ClassroomSchedule.student_id.is_(None)) | (ClassroomSchedule.student_id.in_(student_ids)))
    schedules = query.order_by(ClassroomSchedule.start_time.asc()).all()

    return [
        ScheduleItemResponse(
            id=s.id,
            period_name=s.period_name,
            subject=s.subject,
            start_time=s.start_time,
            end_time=s.end_time,
            visual_icon=s.visual_icon,
            room=s.room,
            instructions=s.instructions,
            is_current=s.is_current
        )
        for s in schedules
    ]

@router.get("/stats")
def get_dashboard_stats(claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """Returns top-level overview metrics for the teacher dashboard."""
    user_id = int(claims["sub"])
    
    role = claims["role"]
    if role == "admin":
        students = db.query(Student).all()
        classes = db.query(Classroom).filter(Classroom.is_active == True).all()
    elif role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        classes = db.query(Classroom).filter(Classroom.teacher_id == teacher.id, Classroom.is_active == True).all() if teacher else []
        student_ids = [row[0] for row in db.query(ClassStudent.student_id).filter(ClassStudent.status == "active", ClassStudent.class_id.in_([c.id for c in classes])).distinct().all()] if classes else []
        students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    elif role == "student":
        student = db.query(Student).filter(Student.user_id == user_id).first()
        students = [student] if student else []
        class_ids = [link.class_id for link in db.query(ClassStudent).filter(ClassStudent.student_id == student.id, ClassStudent.status == "active").all()] if student else []
        classes = db.query(Classroom).filter(Classroom.id.in_(class_ids)).all()
    elif role == "guardian":
        guardian = db.query(Guardian).filter(Guardian.user_id == user_id).first()
        student_ids = [row[0] for row in db.query(GuardianStudent.student_id).filter(GuardianStudent.guardian_id == guardian.id, GuardianStudent.is_authorized == True).all()] if guardian else []
        students = db.query(Student).filter(Student.id.in_(student_ids)).all()
        class_ids = [row[0] for row in db.query(ClassStudent.class_id).filter(ClassStudent.student_id.in_(student_ids), ClassStudent.status == "active").distinct().all()] if student_ids else []
        classes = db.query(Classroom).filter(Classroom.id.in_(class_ids), Classroom.is_active == True).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view platform statistics.")

    student_ids = [student.id for student in students]
    class_ids = [classroom.id for classroom in classes]
    total_students = len(students)
    total_classes = len(classes)
    pending_query = db.query(StudentRequest).filter(StudentRequest.status.in_(["sent", "seen"]))
    if role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        pending_query = pending_query.filter(StudentRequest.teacher_id == teacher.id if teacher else False)
    elif role != "admin":
        pending_query = pending_query.filter(StudentRequest.student_id.in_(student_ids))
    pending_requests = pending_query.count()
    unread_messages = db.query(Message).filter(Message.recipient_id == user_id, Message.is_read == False).count()
    activities = db.query(LearningActivity)
    if role != "admin":
        activities = activities.filter(LearningActivity.class_id.in_(class_ids))
    recent_activities = activities.count()

    return {
        "total_students": total_students,
        "total_classes": total_classes,
        "pending_requests": pending_requests,
        "unread_messages": unread_messages,
        "recent_activities": recent_activities
    }
