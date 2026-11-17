import os
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user_claims
from app.models import (
    Student, User, StudentProfile, CommunicationPreference,
    SupportInstruction, Classroom, ClassStudent, StudentRequest, EmotionCheckin, Teacher,
    Guardian, GuardianStudent, CertificateAuditLog
)
from app.schemas import (
    StudentCardResponse, StudentDetailResponse, CommunicationPreferenceSchema,
    SupportInstructionSchema, DisabilityCertificateInfo, CertificateVerifyRequest,
    CertificateAuditLogResponse
)

router = APIRouter(prefix="/students", tags=["Students"])

ALLOWED_CERTIFICATE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_CERTIFICATE_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg",
}

# -------------------------------------------------------------------------
# Access Permission Helper Functions
# -------------------------------------------------------------------------

def can_teacher_access_student(db: Session, teacher_user_id: int, student_id: int) -> bool:
    """Verifies whether the student is enrolled in at least one class taught by this teacher."""
    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user_id).first()
    if not teacher:
        return False

    enrollment = (
        db.query(ClassStudent)
        .join(Classroom, ClassStudent.class_id == Classroom.id)
        .filter(
            Classroom.teacher_id == teacher.id,
            Classroom.is_active == True,
            ClassStudent.student_id == student_id,
            ClassStudent.status == "active",
        )
        .first()
    )
    return enrollment is not None

def can_guardian_access_student(db: Session, guardian_user_id: int, student_id: int) -> bool:
    """Verifies whether the guardian is authorized for this student."""
    guardian = db.query(Guardian).filter(Guardian.user_id == guardian_user_id).first()
    if not guardian:
        return False

    link = (
        db.query(GuardianStudent)
        .filter(
            GuardianStudent.guardian_id == guardian.id,
            GuardianStudent.student_id == student_id,
            GuardianStudent.is_authorized == True,
        )
        .first()
    )
    return link is not None

def can_user_access_student(db: Session, claims: dict, student_id: int) -> bool:
    role = claims.get("role")
    user_id = int(claims.get("sub", 0))
    if role == "admin":
        return True
    if role == "teacher":
        return can_teacher_access_student(db, user_id, student_id)
    if role == "guardian":
        return can_guardian_access_student(db, user_id, student_id)
    if role == "student":
        student = db.query(Student).filter(Student.id == student_id).first()
        return student is not None and student.user_id == user_id
    return False

def can_user_access_student_certificate(db: Session, claims: dict, student_id: int) -> bool:
    """Checks whether the authenticated user has permission to view/download this student's certificate."""
    role = claims.get("role")
    user_id = int(claims.get("sub", 0))

    return can_user_access_student(db, claims, student_id)

def log_certificate_action(
    db: Session,
    student_id: int,
    user_id: Optional[int],
    user_name: Optional[str],
    user_role: Optional[str],
    action: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
):
    """Writes an immutable compliance audit record for certificate actions."""
    audit_entry = CertificateAuditLog(
        student_id=student_id,
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        action=action,
        details=details,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(audit_entry)
    db.commit()

# -------------------------------------------------------------------------
# Student Endpoints
# -------------------------------------------------------------------------

@router.get("", response_model=List[StudentCardResponse])
def get_students(claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """
    Returns student roster cards for the teacher dashboard.
    Respects privacy: no raw clinical diagnosis labels shown on cards.
    """
    role = claims.get("role")
    user_id = int(claims.get("sub", 0))
    student_query = db.query(Student)
    if role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if not teacher:
            return []
        student_query = student_query.join(ClassStudent).join(Classroom).filter(
            Classroom.teacher_id == teacher.id,
            Classroom.is_active == True,
            ClassStudent.status == "active",
        ).distinct()
    elif role == "guardian":
        guardian = db.query(Guardian).filter(Guardian.user_id == user_id).first()
        if not guardian:
            return []
        student_query = student_query.join(GuardianStudent).filter(
            GuardianStudent.guardian_id == guardian.id,
            GuardianStudent.is_authorized == True,
        )
    elif role == "student":
        student_query = student_query.filter(Student.user_id == user_id)
    elif role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view students.")
    students = student_query.all()
    results = []

    for s in students:
        user = db.query(User).filter(User.id == s.user_id).first()
        if not user:
            continue

        class_links = db.query(ClassStudent).filter(ClassStudent.student_id == s.id).all()
        class_names = []
        for link in class_links:
            cls = db.query(Classroom).filter(Classroom.id == link.class_id).first()
            if cls:
                class_names.append(cls.name)

        pref = db.query(CommunicationPreference).filter(CommunicationPreference.student_id == s.id).first()
        pref_method = "Visual AAC & Symbols"
        if pref:
            if pref.text_to_speech and pref.picture_based_communication:
                pref_method = "Visual AAC + Speech Synthesis"
            elif pref.verbal_communication and not pref.picture_based_communication:
                pref_method = "Verbal & Plain Language"
            elif pref.sign_language:
                pref_method = "Sign Language & Gestures"

        top_inst = db.query(SupportInstruction).filter(
            SupportInstruction.student_id == s.id,
            SupportInstruction.is_active == True
        ).order_by(SupportInstruction.priority.desc()).first()

        pending_count = db.query(StudentRequest).filter(
            StudentRequest.student_id == s.id,
            StudentRequest.status.in_(["sent", "seen"])
        ).count()

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
    return _build_student_detail(student, db, claims)

@router.get("/{student_id}", response_model=StudentDetailResponse)
def get_student_detail(student_id: int, claims: dict = Depends(get_current_user_claims), db: Session = Depends(get_db)):
    """Returns detailed individual student profile including Disability Information & Certificate section."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    if not can_user_access_student(db, claims, student_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this student.")
    
    # Audit log entry for teacher or admin accessing student details
    user_id = int(claims.get("sub", 0))
    role = claims.get("role")
    name = claims.get("name", "User")
    if role in ["teacher", "admin"]:
        log_certificate_action(
            db=db,
            student_id=student.id,
            user_id=user_id,
            user_name=name,
            user_role=role,
            action="view_details",
            details=f"Viewed profile of student {student.student_code}"
        )

    return _build_student_detail(student, db, claims)

def _build_student_detail(student: Student, db: Session, claims: Optional[dict] = None) -> StudentDetailResponse:
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

    # Disability Information & Certificate section mapping
    disability_info = None
    if profile:
        can_access = can_user_access_student_certificate(db, claims, student.id) if claims else False
        has_cert = bool(profile.certificate_file_path and profile.certificate_filename)
        
        disability_info = DisabilityCertificateInfo(
            disability_type=profile.disability_type,
            disability_description=profile.disability_description,
            has_certificate=has_cert,
            certificate_filename=profile.certificate_filename if has_cert else None,
            certificate_mime_type=profile.certificate_mime_type if has_cert else None,
            certificate_file_size=profile.certificate_file_size if has_cert else None,
            certificate_uploaded_at=profile.certificate_uploaded_at if has_cert else None,
            certificate_verification_status=profile.certificate_verification_status or "unsubmitted",
            certificate_verification_notes=profile.certificate_verification_notes,
            certificate_verified_at=profile.certificate_verified_at,
            can_access_certificate=can_access and has_cert,
        )

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
        classes=class_names,
        disability_info=disability_info,
    )

# -------------------------------------------------------------------------
# Certificate Upload & Access Endpoints
# -------------------------------------------------------------------------

@router.post("/{student_id}/certificate")
async def upload_certificate(
    student_id: int,
    request: Request,
    file: UploadFile = File(...),
    disability_type: str = Form(...),
    disability_description: Optional[str] = Form(None),
    claims: dict = Depends(get_current_user_claims),
    db: Session = Depends(get_db),
):
    """
    Allows ONLY authorized guardians (or administrators) to upload a disability certificate.
    Teachers CANNOT upload or certify medical documents.
    """
    role = claims.get("role")
    user_id = int(claims.get("sub", 0))
    user_name = claims.get("name", "User")

    if role != "guardian" or not can_guardian_access_student(db, user_id, student_id):
        raise HTTPException(status_code=403, detail="Only a guardian authorized for this student can upload or replace a certificate.")

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.MAX_CERTIFICATE_SIZE_BYTES + 64 * 1024:
                raise HTTPException(status_code=413, detail="Certificate upload exceeds the maximum request size.")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Content-Length header.")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Validate file extension
    original_filename = (file.filename or "certificate").replace("\\", "/").split("/")[-1][:255]
    _, ext = os.path.splitext(original_filename.lower())
    if ext not in ALLOWED_CERTIFICATE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: PDF, JPG, JPEG, PNG.",
        )

    # Validate MIME type
    content_type = file.content_type or ""
    if content_type.lower() not in ALLOWED_CERTIFICATE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported MIME type '{content_type}'. Must be PDF, JPG, or PNG.",
        )

    expected_types = {
        ".pdf": {"application/pdf"},
        ".jpg": {"image/jpeg", "image/jpg"},
        ".jpeg": {"image/jpeg", "image/jpg"},
        ".png": {"image/png"},
    }
    if content_type.lower() not in expected_types[ext]:
        raise HTTPException(status_code=400, detail="File extension and MIME type do not match.")

    # Bounded read limits memory and rejects oversized bodies without loading the full upload.
    file_bytes = await file.read(settings.MAX_CERTIFICATE_SIZE_BYTES + 1)
    file_size = len(file_bytes)
    if file_size > settings.MAX_CERTIFICATE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_CERTIFICATE_SIZE_BYTES // (1024*1024)} MB.",
        )
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    signatures = {
        ".pdf": file_bytes.startswith(b"%PDF-"),
        ".jpg": file_bytes.startswith(b"\xff\xd8\xff"),
        ".jpeg": file_bytes.startswith(b"\xff\xd8\xff"),
        ".png": file_bytes.startswith(b"\x89PNG\r\n\x1a\n"),
    }
    if not signatures[ext]:
        raise HTTPException(status_code=400, detail="File content does not match the declared certificate format.")

    if not disability_type.strip() or len(disability_type) > 100 or (disability_description and len(disability_description) > 4000):
        raise HTTPException(status_code=400, detail="Disability type or description is invalid or too long.")

    storage_dir = Path(settings.CERTIFICATES_STORAGE_DIR).resolve()
    storage_dir.mkdir(parents=True, exist_ok=True)
    secure_filename = f"cert_stu_{student_id}_{uuid.uuid4().hex}{ext}"
    destination = storage_dir / secure_filename
    destination_path = str(destination)
    previous_path = None
    prior_profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if prior_profile:
        previous_path = prior_profile.certificate_file_path

    with open(destination_path, "xb") as f:
        f.write(file_bytes)

    # Update StudentProfile
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if not profile:
        profile = StudentProfile(student_id=student_id)
        db.add(profile)

    profile.disability_type = disability_type.strip()
    profile.disability_description = disability_description.strip() if disability_description else None
    profile.certificate_filename = original_filename
    profile.certificate_file_path = destination_path
    profile.certificate_mime_type = content_type
    profile.certificate_file_size = file_size
    profile.certificate_uploaded_at = datetime.utcnow()
    profile.certificate_uploaded_by_user_id = user_id
    profile.certificate_verification_status = "pending"  # Always resets to pending on upload
    profile.certificate_verified_by_user_id = None
    profile.certificate_verification_notes = None
    profile.certificate_verified_at = None

    try:
        db.commit()
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    db.refresh(profile)
    if previous_path and previous_path != destination_path:
        previous = Path(previous_path).resolve()
        if previous.is_relative_to(storage_dir) and previous.is_file():
            previous.unlink(missing_ok=True)

    # Audit log
    client_ip = request.client.host if request.client else "unknown"
    log_certificate_action(
        db=db,
        student_id=student_id,
        user_id=user_id,
        user_name=user_name,
        user_role=role,
        action="upload",
        details=f"Certificate upload recorded ({file_size} bytes).",
        ip_address=client_ip,
    )

    return {
        "status": "success",
        "message": "Certificate uploaded successfully and submitted for administrator verification.",
        "disability_type": profile.disability_type,
        "certificate_filename": profile.certificate_filename,
        "verification_status": profile.certificate_verification_status,
        "upload_date": profile.certificate_uploaded_at,
    }

@router.get("/{student_id}/certificate/download")
def download_certificate(
    student_id: int,
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    db: Session = Depends(get_db),
):
    """
    Securely opens / downloads the student's disability certificate.
    Teachers must ONLY access certificates belonging to students in their classes.
    """
    if not can_user_access_student_certificate(db, claims, student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: this account is not authorized to access the student's certificate.",
        )

    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if not profile or not profile.certificate_file_path:
        raise HTTPException(status_code=404, detail="No certificate file found for this student.")
    storage_dir = Path(settings.CERTIFICATES_STORAGE_DIR).resolve()
    certificate_path = Path(profile.certificate_file_path).resolve()
    if not certificate_path.is_relative_to(storage_dir) or not certificate_path.is_file():
        raise HTTPException(status_code=404, detail="No certificate file found for this student.")

    # Record download in audit log
    user_id = int(claims.get("sub", 0))
    user_name = claims.get("name", "User")
    user_role = claims.get("role", "unknown")
    client_ip = request.client.host if request.client else "unknown"

    log_certificate_action(
        db=db,
        student_id=student_id,
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        action="download",
        details="Authorized certificate download recorded.",
        ip_address=client_ip,
    )

    return FileResponse(
        path=str(certificate_path),
        filename=profile.certificate_filename,
        media_type=profile.certificate_mime_type or "application/octet-stream",
        headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"},
    )

@router.post("/{student_id}/certificate/verify")
def verify_certificate(
    student_id: int,
    payload: CertificateVerifyRequest,
    request: Request,
    claims: dict = Depends(get_current_user_claims),
    db: Session = Depends(get_db),
):
    """
    Certificate verification MUST only be performed by an authorized school administrator.
    Teachers can view verification status but cannot independently certify medical documents.
    """
    role = claims.get("role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an authorized school administrator can verify or reject disability certificates.",
        )

    target_status = payload.status.lower().strip()
    if target_status not in ["verified", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'verified' or 'rejected'.",
        )

    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if not profile or not profile.certificate_filename:
        raise HTTPException(status_code=404, detail="No certificate exists to verify.")

    user_id = int(claims.get("sub", 0))
    user_name = claims.get("name", "Administrator")

    profile.certificate_verification_status = target_status
    profile.certificate_verified_by_user_id = user_id
    profile.certificate_verification_notes = payload.notes
    profile.certificate_verified_at = datetime.utcnow()

    db.commit()
    db.refresh(profile)

    # Record in audit log
    client_ip = request.client.host if request.client else "unknown"
    log_certificate_action(
        db=db,
        student_id=student_id,
        user_id=user_id,
        user_name=user_name,
        user_role=role,
        action=target_status,
        details=f"Certificate {target_status} by administrator. Notes: {payload.notes or 'None'}",
        ip_address=client_ip,
    )

    return {
        "status": "success",
        "verification_status": profile.certificate_verification_status,
        "verified_at": profile.certificate_verified_at,
        "notes": profile.certificate_verification_notes,
    }

@router.get("/{student_id}/certificate/audit-logs", response_model=List[CertificateAuditLogResponse])
def get_certificate_audit_logs(
    student_id: int,
    claims: dict = Depends(get_current_user_claims),
    db: Session = Depends(get_db),
):
    """Retrieves access and upload audit logs for authorized staff or administrators."""
    if not can_user_access_student_certificate(db, claims, student_id):
        raise HTTPException(status_code=403, detail="Not authorized to inspect audit logs for this student.")

    logs = (
        db.query(CertificateAuditLog)
        .filter(CertificateAuditLog.student_id == student_id)
        .order_by(CertificateAuditLog.created_at.desc())
        .limit(50)
        .all()
    )
    return logs
