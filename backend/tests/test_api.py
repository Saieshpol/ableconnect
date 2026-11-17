import pytest
from fastapi.testclient import TestClient
from app.main import app

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

def test_demo_switch():
    response = client.post("/api/auth/demo-switch", json={
        "target_role": "guardian"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "guardian"

def test_aac_sentence_synthesis():
    response = client.post("/api/communication/synthesize-sentence", json={
        "symbols": ["I", "Need", "Help"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["sentence"] == "I need help."

def test_instruction_simplifier():
    response = client.post("/api/tools/simplify", json={
        "original_text": "Complete the exercise in your notebook and submit it before the end of the session."
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["steps"]) >= 2
    assert "audio_ready_text" in data

def test_get_boards():
    response = client.get("/api/communication/boards")
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
