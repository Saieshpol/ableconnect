from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models import (
    CommunicationBoard, CommunicationSymbol, StudentRequest, EmotionCheckin,
    Message, User, Student, Teacher
)
from app.schemas import (
    BoardSchema, SymbolSchema, SentenceSynthesizeRequest, SentenceSynthesizeResponse,
    StudentRequestCreate, StudentRequestResponse, StudentRequestUpdate,
    EmotionCheckinCreate, EmotionCheckinResponse, MessageCreate, MessageResponse
)
from app.services.aac_service import AACService

router = APIRouter(prefix="/communication", tags=["Communication"])

@router.get("/boards", response_model=List[BoardSchema])
def get_boards(student_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Fetches communication boards with their symbols for visual AAC."""
    boards = db.query(CommunicationBoard).all()
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
def synthesize_sentence(payload: SentenceSynthesizeRequest):
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

    # Find teacher assigned if available
    teacher = db.query(Teacher).first()

    req = StudentRequest(
        student_id=student.id,
        teacher_id=teacher.id if teacher else None,
        class_id=payload.class_id,
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
    else:
        # Teacher or guardian
        requests = db.query(StudentRequest).order_by(StudentRequest.created_at.desc()).limit(50).all()

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
        query = query.filter(
            (Message.sender_id == partner_id) | (Message.recipient_id == partner_id)
        )

    messages = query.order_by(Message.created_at.asc()).limit(100).all()
    results = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        recipient = db.query(User).filter(User.id == m.recipient_id).first()
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
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found.")

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

    sender = db.query(User).filter(User.id == user_id).first()
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
