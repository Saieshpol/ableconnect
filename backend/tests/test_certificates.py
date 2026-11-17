import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token(role: str, student_id: int = None) -> str:
    credentials = {
        "teacher": ("teacher@ableconnect.org", "teacher123"),
        "student": ("leo@ableconnect.org" if student_id != 2 else "maya@ableconnect.org", "student123"),
        "guardian": ("guardian@ableconnect.org", "guardian123"),
        "admin": ("admin@ableconnect.org", "admin123"),
    }
    email, password = credentials[role]
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_teacher_can_view_assigned_student_disability_info():
    """Teacher Sarah can view Leo Vance's disability info & certificate details (Leo is in Room 102)."""
    teacher_token = get_token("teacher")
    res = client.get("/api/students/1", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "disability_info" in data
    d_info = data["disability_info"]
    assert d_info["disability_type"] == "Speech & Communication Impairment"
    assert d_info["has_certificate"] is True
    assert d_info["certificate_verification_status"] == "verified"
    assert d_info["can_access_certificate"] is True
    assert d_info["certificate_filename"] == "leo_vance_speech_evaluation_report.pdf"

def test_teacher_can_download_assigned_student_certificate():
    """Teacher Sarah can securely download Leo Vance's certificate."""
    teacher_token = get_token("teacher")
    res = client.get("/api/students/1/certificate/download", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.headers["cache-control"] == "private, no-store"
    assert len(res.content) > 0

def test_teacher_cannot_download_unassigned_student_certificate():
    """
    Teacher Sarah CANNOT download Chloe Kim's certificate (Chloe is in Room 204 under Mr. Adams,
    not in any class taught by Sarah).
    """
    teacher_token = get_token("teacher")
    res = client.get("/api/students/4/certificate/download", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]

def test_teacher_cannot_upload_certificate():
    """Teachers cannot upload or replace medical certificates."""
    teacher_token = get_token("teacher")
    dummy_pdf = io.BytesIO(b"%PDF-1.4 dummy content")
    res = client.post(
        "/api/students/1/certificate",
        headers={"Authorization": f"Bearer {teacher_token}"},
        data={"disability_type": "Hearing Impairment"},
        files={"file": ("test.pdf", dummy_pdf, "application/pdf")}
    )
    assert res.status_code == 403
    assert "Only a guardian authorized" in res.json()["detail"]

def test_teacher_cannot_verify_certificate():
    """Teachers cannot independently certify or verify medical documents."""
    teacher_token = get_token("teacher")
    res = client.post(
        "/api/students/2/certificate/verify",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"status": "verified", "notes": "Approved by teacher"}
    )
    assert res.status_code == 403
    assert "Only an authorized school administrator can verify" in res.json()["detail"]

def test_authorized_guardian_can_upload_certificate():
    """Authorized Guardian David Chen can upload a certificate for Leo Vance."""
    guardian_token = get_token("guardian")
    dummy_pdf = io.BytesIO(b"%PDF-1.4 new evaluation content")
    res = client.post(
        "/api/students/1/certificate",
        headers={"Authorization": f"Bearer {guardian_token}"},
        data={
            "disability_type": "Speech & Communication Impairment",
            "disability_description": "Updated speech therapy evaluation."
        },
        files={"file": ("updated_speech_report.pdf", dummy_pdf, "application/pdf")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["verification_status"] == "pending"

def test_unauthorized_guardian_cannot_upload_for_other_student():
    """Guardian David Chen CANNOT upload a certificate for Maya Patel (not his child)."""
    guardian_token = get_token("guardian")
    dummy_pdf = io.BytesIO(b"%PDF-1.4 dummy content")
    res = client.post(
        "/api/students/2/certificate",
        headers={"Authorization": f"Bearer {guardian_token}"},
        data={"disability_type": "Sensory Sensitivity"},
        files={"file": ("unauthorized.pdf", dummy_pdf, "application/pdf")}
    )
    assert res.status_code == 403
    assert "Only a guardian authorized" in res.json()["detail"]

def test_administrator_can_verify_certificate():
    """Administrator Dr. Eleanor Vance can verify or reject a pending certificate."""
    admin_token = get_token("admin")
    res = client.post(
        "/api/students/1/certificate/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "verified", "notes": "Verified by school administrative board."}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["verification_status"] == "verified"
    assert data["notes"] == "Verified by school administrative board."

def test_audit_logs_recorded():
    """Audit logs must record certificate actions for compliance."""
    admin_token = get_token("admin")
    res = client.get("/api/students/1/certificate/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    actions = [log["action"] for log in logs]
    assert "upload" in actions or "verify" in actions

def test_certificate_upload_rejects_mismatched_file_signature():
    guardian_token = get_token("guardian")
    res = client.post(
        "/api/students/1/certificate",
        headers={"Authorization": f"Bearer {guardian_token}"},
        data={"disability_type": "Declared support information"},
        files={"file": ("fake.pdf", io.BytesIO(b"not a pdf"), "application/pdf")},
    )
    assert res.status_code == 400
    assert "content does not match" in res.json()["detail"]

def test_student_cannot_read_unrelated_student_profile():
    student_token = get_token("student", 1)
    res = client.get("/api/students/2", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 403

def test_teacher_cannot_read_unassigned_student_profile():
    teacher_token = get_token("teacher")
    res = client.get("/api/students/4", headers={"Authorization": f"Bearer {teacher_token}"})
    assert res.status_code == 403

def test_guardian_cannot_read_unauthorized_child_profile():
    guardian_token = get_token("guardian")
    res = client.get("/api/students/2", headers={"Authorization": f"Bearer {guardian_token}"})
    assert res.status_code == 403
