import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import Settings
from pydantic import ValidationError

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AbleConnect" in data["app"]

def test_teacher_login():
    response = client.post("/api/auth/login", json={
        "email": "teacher@ableconnect.org",
        "password": "teacher123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "teacher"
    assert data["user"]["full_name"] == "Sarah Jenkins, M.Ed."

def test_student_login():
    response = client.post("/api/auth/login", json={
        "email": "leo@ableconnect.org",
        "password": "student123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "student"

def test_demo_switch_endpoint_removed():
    response = client.post("/api/auth/demo-switch", json={"target_role": "admin"})
    assert response.status_code == 404

def test_aac_sentence_synthesis():
    login = client.post("/api/auth/login", json={"email": "leo@ableconnect.org", "password": "student123"})
    token = login.json()["access_token"]
    response = client.post("/api/communication/synthesize-sentence", json={
        "symbols": ["I", "Need", "Help"]
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["sentence"] == "I need help."

def test_instruction_simplifier():
    login = client.post("/api/auth/login", json={"email": "teacher@ableconnect.org", "password": "teacher123"})
    token = login.json()["access_token"]
    response = client.post("/api/tools/simplify", json={
        "original_text": "Complete the exercise in your notebook and submit it before the end of the session."
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["steps"]) >= 2
    assert "audio_ready_text" in data

def test_get_boards():
    login = client.post("/api/auth/login", json={"email": "leo@ableconnect.org", "password": "student123"})
    response = client.get("/api/communication/boards", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert response.status_code == 200
    boards = response.json()
    assert len(boards) >= 1
    # Check symbols attached
    assert any(len(b["symbols"]) > 0 for b in boards)

def test_get_students_list():
    # Login as teacher first
    login_res = client.post("/api/auth/login", json={
        "email": "teacher@ableconnect.org",
        "password": "teacher123"
    })
    token = login_res.json()["access_token"]
    
    response = client.get("/api/students", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    students = response.json()
    assert len(students) >= 3
    # Check that privacy rule holds: no sensitive diagnosis field in student cards
    for s in students:
        assert "diagnosis" not in s
        assert "full_name" in s
        assert "preferred_communication" in s

def test_teacher_roster_excludes_students_outside_assigned_classes():
    login = client.post("/api/auth/login", json={"email": "teacher@ableconnect.org", "password": "teacher123"})
    res = client.get("/api/students", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert res.status_code == 200
    assert 4 not in {student["id"] for student in res.json()}

def test_sensitive_routes_require_authentication():
    assert client.get("/api/communication/boards").status_code == 401
    assert client.get("/api/classes").status_code == 401
    assert client.post("/api/communication/synthesize-sentence", json={"symbols": ["help"]}).status_code == 401
    assert client.post("/api/tools/simplify", json={"original_text": "hello"}).status_code == 401

def test_production_settings_reject_unsafe_configuration():
    strong_secret = "rT7_93T4lJX7qV0chPsT_0X9BY6zoI5bLYj2mwpzO5K7cEn2"
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="production", JWT_SECRET_KEY=strong_secret,
            DATABASE_URL="sqlite:///./ableconnect.db", CORS_ORIGINS="https://ableconnect.example",
            CERTIFICATES_STORAGE_DIR="/var/data/certificates",
        )
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="production", JWT_SECRET_KEY=strong_secret,
            DATABASE_URL="postgresql://user:pass@db.example/ableconnect", CORS_ORIGINS="*",
            CERTIFICATES_STORAGE_DIR="/var/data/certificates",
        )
