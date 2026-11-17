from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models import (
    ClassroomSchedule, Classroom, Student, StudentRequest, Message, LearningActivity, ClassStudent
)
from app.schemas import (
    SimplifyRequest, SimplifyResponse, SimplifiedStep, ScheduleItemResponse
)
from app.services.simplifier import InstructionSimplifier

router = APIRouter(prefix="/tools", tags=["Pedagogical Tools"])

@router.post("/simplify", response_model=SimplifyResponse)
async def simplify_instruction(payload: SimplifyRequest):
    """
    Simplifies compound classroom instructions into step-by-step
    accessible items with visual icon cues and speech-ready text.
    """
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
    if class_id:
        query = query.filter(ClassroomSchedule.class_id == class_id)
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
    
    total_students = db.query(Student).count()
    total_classes = db.query(Classroom).count()
    pending_requests = db.query(StudentRequest).filter(StudentRequest.status.in_(["sent", "seen"])).count()
    unread_messages = db.query(Message).filter(Message.recipient_id == user_id, Message.is_read == False).count()
    recent_activities = db.query(LearningActivity).count()

    return {
        "total_students": total_students,
        "total_classes": total_classes,
        "pending_requests": pending_requests,
        "unread_messages": unread_messages,
        "recent_activities": recent_activities
    }
