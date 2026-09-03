import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models import User, UserRole

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_budgetbuddy.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

def create_user_and_get_token(client, email="user@example.com", name="Test User", password="password123", role="student"):
    client.post("/api/v1/auth/register", json={"email": email, "full_name": name, "password": password, "role": role})
    db = TestingSessionLocal()
    usr = db.query(User).filter(User.email == email).first()
    usr.is_email_verified = True
    usr.role = role
    db.commit()
    db.close()

    formData = {"username": email, "password": password}
    resp = client.post("/api/v1/auth/login", data=formData)
    return resp.json()["access_token"]
