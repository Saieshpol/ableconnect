from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models import (
    CommunicationBoard, CommunicationSymbol, StudentRequest, EmotionCheckin,
    Message, User, Student, Teacher, Classroom, ClassStudent, Guardian, GuardianStudent
)
from app.schemas import (
    BoardSchema, SymbolSchema, SentenceSynthesizeRequest, SentenceSynthesizeResponse,
    StudentRequestCreate, StudentRequestResponse, StudentRequestUpdate,
    EmotionCheckinCreate, EmotionCheckinResponse, MessageCreate, MessageResponse
)
from app.services.aac_service import AACService

router = APIRouter(prefix="/communication", tags=["Communication"])

def _is_allowed_pair(db: Session, user_a: User, user_b: User) -> bool:
    if user_a.id == user_b.id:
        return False
    roles = {user_a.role, user_b.role}
    if roles == {"teacher", "student"}:
        teacher, student_user = (user_a, user_b) if user_a.role == "teacher" else (user_b, user_a)
        teacher_profile = db.query(Teacher).filter(Teacher.user_id == teacher.id).first()
        student = db.query(Student).filter(Student.user_id == student_user.id).first()
        return bool(teacher_profile and student and db.query(ClassStudent).join(Classroom).filter(
            ClassStudent.student_id == student.id, ClassStudent.status == "active",
            Classroom.teacher_id == teacher_profile.id, Classroom.is_active == True,
        ).first())
    if roles == {"guardian", "student"}:
        guardian_user, student_user = (user_a, user_b) if user_a.role == "guardian" else (user_b, user_a)
        guardian = db.query(Guardian).filter(Guardian.user_id == guardian_user.id).first()
        student = db.query(Student).filter(Student.user_id == student_user.id).first()
        return bool(guardian and student and db.query(GuardianStudent).filter(
            GuardianStudent.guardian_id == guardian.id, GuardianStudent.student_id == student.id,
            GuardianStudent.is_authorized == True,
        ).first())
    if roles == {"teacher", "guardian"}:
        teacher_user, guardian_user = (user_a, user_b) if user_a.role == "teacher" else (user_b, user_a)
        teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user.id).first()
        guardian = db.query(Guardian).filter(Guardian.user_id == guardian_user.id).first()
        return bool(teacher and guardian and db.query(GuardianStudent).join(ClassStudent, ClassStudent.student_id == GuardianStudent.student_id).join(Classroom, Classroom.id == ClassStudent.class_id).filter(
            GuardianStudent.guardian_id == guardian.id, GuardianStudent.is_authorized == True,
            ClassStudent.status == "active", Classroom.is_active == True, Classroom.teacher_id == teacher.id,
        ).first())
    return False

@router.get("/boards", response_model=List[BoardSchema])
def get_boards(claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """Fetches communication boards with their symbols for visual AAC."""
    role = claims["role"]
    user_id = int(claims["sub"])
    query = db.query(CommunicationBoard).filter(CommunicationBoard.is_default == True)
    if role == "admin":
        query = db.query(CommunicationBoard)
    elif role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if teacher:
            query = db.query(CommunicationBoard).filter(
                (CommunicationBoard.is_default == True) | (CommunicationBoard.teacher_id == teacher.id)
            )
    elif role == "student":
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if student:
            query = db.query(CommunicationBoard).filter(
                (CommunicationBoard.is_default == True) | (CommunicationBoard.student_id == student.id)
            )
    boards = query.all()
    results = []
    for b in boards:
        symbols = db.query(CommunicationSymbol).filter(
            CommunicationSymbol.board_id == b.id
        ).order_by(CommunicationSymbol.position_order).all()

        symbol_schemas = [
            SymbolSchema(
                id=s.id,
                label=s.label,
                icon_name=s.icon_name,
                speech_text=s.speech_text,
                category=s.category,
                position_order=s.position_order,
                bg_color=s.bg_color,
                border_color=s.border_color
            )
            for s in symbols
        ]

        results.append(
            BoardSchema(
                id=b.id,
                title=b.title,
                description=b.description,
                category=b.category,
                grid_columns=b.grid_columns,
                is_default=b.is_default,
                symbols=symbol_schemas
            )
        )
    return results

@router.post("/synthesize-sentence", response_model=SentenceSynthesizeResponse)
def synthesize_sentence(payload: SentenceSynthesizeRequest, claims: dict = Depends(get_current_user_claims)):
    """Turns selected picture card tokens into a natural spoken sentence."""
    result = AACService.synthesize_sentence(payload.symbols)
    return SentenceSynthesizeResponse(
        sentence=result["sentence"],
        spoken_text=result["spoken_text"],
        category=result["category"]
    )

# Dignified Student Help Requests
@router.post("/requests", response_model=StudentRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(payload: StudentRequestCreate, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    user_id = int(claims["sub"])
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Only students can submit help requests.")

    enrollments = db.query(ClassStudent).join(Classroom).filter(
        ClassStudent.student_id == student.id, ClassStudent.status == "active", Classroom.is_active == True
    )
    if payload.class_id is not None:
        enrollments = enrollments.filter(ClassStudent.class_id == payload.class_id)
    enrollment = enrollments.first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Student is not enrolled in the requested class.")
    classroom = db.query(Classroom).filter(Classroom.id == enrollment.class_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == classroom.teacher_id).first() if classroom else None

    req = StudentRequest(
        student_id=student.id,
        teacher_id=teacher.id if teacher else None,
        class_id=enrollment.class_id,
        request_type=payload.request_type,
        message=payload.message or f"Student requested: {payload.request_type}",
        status="sent",
        created_at=datetime.utcnow()
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    user = db.query(User).filter(User.id == student.user_id).first()
    return StudentRequestResponse(
        id=req.id,
        student_id=req.student_id,
        student_name=user.full_name if user else "Student",
        teacher_id=req.teacher_id,
        class_id=req.class_id,
        request_type=req.request_type,
        message=req.message,
        status=req.status,
        response_notes=req.response_notes,
        created_at=req.created_at,
        responded_at=req.responded_at
    )

@router.get("/requests", response_model=List[StudentRequestResponse])
def get_requests(claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    user_id = int(claims["sub"])
    role = claims["role"]

    if role == "student":
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            return []
        requests = db.query(StudentRequest).filter(
            StudentRequest.student_id == student.id
        ).order_by(StudentRequest.created_at.desc()).all()
    elif role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        requests = db.query(StudentRequest).filter(StudentRequest.teacher_id == teacher.id).order_by(StudentRequest.created_at.desc()).limit(50).all() if teacher else []
    elif role == "guardian":
        guardian = db.query(Guardian).filter(Guardian.user_id == user_id).first()
        requests = db.query(StudentRequest).join(GuardianStudent, GuardianStudent.student_id == StudentRequest.student_id).filter(
            GuardianStudent.guardian_id == guardian.id if guardian else False,
            GuardianStudent.is_authorized == True,
        ).order_by(StudentRequest.created_at.desc()).limit(50).all() if guardian else []
    elif role == "admin":
        requests = db.query(StudentRequest).order_by(StudentRequest.created_at.desc()).limit(50).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view requests.")

    results = []
    for r in requests:
        student = db.query(Student).filter(Student.id == r.student_id).first()
        student_name = "Student"
        if student:
            user = db.query(User).filter(User.id == student.user_id).first()
            if user:
                student_name = user.full_name

        results.append(
            StudentRequestResponse(
                id=r.id,
                student_id=r.student_id,
                student_name=student_name,
                teacher_id=r.teacher_id,
                class_id=r.class_id,
                request_type=r.request_type,
                message=r.message,
                status=r.status,
                response_notes=r.response_notes,
                created_at=r.created_at,
                responded_at=r.responded_at
            )
        )
    return results

@router.patch("/requests/{request_id}", response_model=StudentRequestResponse)
def update_request_status(request_id: int, payload: StudentRequestUpdate, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    req = db.query(StudentRequest).filter(StudentRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found.")

    role = claims["role"]
    user_id = int(claims["sub"])
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first() if role == "teacher" else None
    if role != "admin" and (not teacher or req.teacher_id != teacher.id):
        raise HTTPException(status_code=403, detail="Only the assigned teacher or an administrator can respond to this request.")
    if payload.status not in {"seen", "responded", "resolved"}:
        raise HTTPException(status_code=400, detail="Invalid request status.")

    req.status = payload.status
    if payload.response_notes:
        req.response_notes = payload.response_notes
    if payload.status in ["responded", "resolved"]:
        req.responded_at = datetime.utcnow()

    db.commit()
    db.refresh(req)

    student = db.query(Student).filter(Student.id == req.student_id).first()
    student_name = "Student"
    if student:
        user = db.query(User).filter(User.id == student.user_id).first()
        if user:
            student_name = user.full_name

    return StudentRequestResponse(
        id=req.id,
        student_id=req.student_id,
        student_name=student_name,
        teacher_id=req.teacher_id,
        class_id=req.class_id,
        request_type=req.request_type,
        message=req.message,
        status=req.status,
        response_notes=req.response_notes,
        created_at=req.created_at,
        responded_at=req.responded_at
    )

# Emotion Check-in
@router.post("/emotions", response_model=EmotionCheckinResponse, status_code=status.HTTP_201_CREATED)
def submit_emotion_checkin(payload: EmotionCheckinCreate, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    user_id = int(claims["sub"])
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Only students can submit emotion check-ins.")

    if payload.class_id is not None and not db.query(ClassStudent).filter(
        ClassStudent.student_id == student.id, ClassStudent.class_id == payload.class_id,
        ClassStudent.status == "active",
    ).first():
        raise HTTPException(status_code=403, detail="Student is not enrolled in the selected class.")

    checkin = EmotionCheckin(
        student_id=student.id,
        class_id=payload.class_id,
        emotion=payload.emotion,
        notes=payload.notes,
        energy_level=payload.energy_level,
        created_at=datetime.utcnow()
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    return EmotionCheckinResponse(
        id=checkin.id,
        student_id=checkin.student_id,
        emotion=checkin.emotion,
        notes=checkin.notes,
        energy_level=checkin.energy_level,
        created_at=checkin.created_at
    )

# Two-Way Messaging
@router.get("/messages", response_model=List[MessageResponse])
def get_messages(partner_id: Optional[int] = None, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    user_id = int(claims["sub"])
    query = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.recipient_id == user_id)
    )
    if partner_id:
        partner = db.query(User).filter(User.id == partner_id, User.is_active == True).first()
        current = db.query(User).filter(User.id == user_id).first()
        if not partner or not current or not _is_allowed_pair(db, current, partner):
            raise HTTPException(status_code=403, detail="Not authorized to view this conversation.")
        query = query.filter(
            (Message.sender_id == partner_id) | (Message.recipient_id == partner_id)
        )

    messages = query.order_by(Message.created_at.asc()).limit(100).all()
    current = db.query(User).filter(User.id == user_id).first()
    results = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        recipient = db.query(User).filter(User.id == m.recipient_id).first()
        partner = recipient if m.sender_id == user_id else sender
        if not current or not partner or not _is_allowed_pair(db, current, partner):
            continue
        results.append(
            MessageResponse(
                id=m.id,
                sender_id=m.sender_id,
                sender_name=sender.full_name if sender else "User",
                recipient_id=m.recipient_id,
                recipient_name=recipient.full_name if recipient else "User",
                content=m.content,
                message_type=m.message_type,
                attachments=m.attachments,
                is_read=m.is_read,
                created_at=m.created_at
            )
        )
    return results

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(payload: MessageCreate, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    user_id = int(claims["sub"])
    recipient = db.query(User).filter(User.id == payload.recipient_id).first()
    if not recipient or not recipient.is_active:
        raise HTTPException(status_code=404, detail="Recipient user not found.")
    sender = db.query(User).filter(User.id == user_id).first()
    if not sender or not _is_allowed_pair(db, sender, recipient):
        raise HTTPException(status_code=403, detail="You are not an authorized contact for this user.")

    msg = Message(
        sender_id=user_id,
        recipient_id=payload.recipient_id,
        content=payload.content,
        message_type=payload.message_type or "text",
        attachments=payload.attachments,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return MessageResponse(
        id=msg.id,
        sender_id=msg.sender_id,
        sender_name=sender.full_name if sender else "User",
        recipient_id=msg.recipient_id,
        recipient_name=recipient.full_name,
        content=msg.content,
        message_type=msg.message_type,
        attachments=msg.attachments,
        is_read=msg.is_read,
        created_at=msg.created_at
    )
