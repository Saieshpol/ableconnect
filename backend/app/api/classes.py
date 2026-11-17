from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models import Classroom, Teacher, ClassStudent, User
from app.schemas import ClassroomResponse, ClassroomCreate

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("", response_model=List[ClassroomResponse])
def get_classes(claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    user_id = int(claims["sub"])
    role = claims["role"]

    if role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if not teacher:
            return []
        classes = db.query(Classroom).filter(Classroom.teacher_id == teacher.id).all()
    else:
        # If student or guardian, return active classes
        classes = db.query(Classroom).filter(Classroom.is_active == True).all()

    result = []
    for c in classes:
        student_count = db.query(ClassStudent).filter(ClassStudent.class_id == c.id, ClassStudent.status == "active").count()
        result.append(
            ClassroomResponse(
                id=c.id,
                name=c.name,
                grade_level=c.grade_level,
                section=c.section,
                room=c.room,
                schedule_summary=c.schedule_summary,
                color_theme=c.color_theme,
                student_count=student_count,
                is_active=c.is_active,
                created_at=c.created_at
            )
        )
    return result

@router.post("", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
def create_class(payload: ClassroomCreate, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    user_id = int(claims["sub"])
    role = claims["role"]

    if role != "teacher" and role != "admin":
        raise HTTPException(status_code=403, detail="Only teachers can create classes.")

    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="Teacher profile not found for current user.")

    new_class = Classroom(
        teacher_id=teacher.id,
        name=payload.name,
        grade_level=payload.grade_level,
        section=payload.section,
        room=payload.room,
        color_theme=payload.color_theme or "teal",
        is_active=True
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return ClassroomResponse(
        id=new_class.id,
        name=new_class.name,
        grade_level=new_class.grade_level,
        section=new_class.section,
        room=new_class.room,
        schedule_summary=new_class.schedule_summary,
        color_theme=new_class.color_theme,
        student_count=0,
        is_active=new_class.is_active,
        created_at=new_class.created_at
    )
