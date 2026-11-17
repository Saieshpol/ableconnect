import sys
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Isolated local-only test configuration; never used by Render production.
os.environ["ENVIRONMENT"] = "development"
os.environ["JWT_SECRET_KEY"] = "test-only-4b2d1d42-9b8e-43f1-8e76-0a513c3a9f71"
TEST_DATA_DIR = tempfile.mkdtemp(prefix="ableconnect-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(TEST_DATA_DIR, "ableconnect.db").replace("\\", "/")
os.environ["SEED_DEMO_DATA"] = "true"
os.environ["AUTO_CREATE_SCHEMA"] = "true"
os.environ["CERTIFICATES_STORAGE_DIR"] = os.path.join(TEST_DATA_DIR, "certificates")

@pytest.fixture(scope="session", autouse=True)
def initialize_test_application():
    from app.main import app
    with TestClient(app):
        yield
