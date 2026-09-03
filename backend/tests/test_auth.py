import pytest
from app.models import User
from tests.conftest import TestingSessionLocal, create_user_and_get_token

def test_user_registration(client):
    resp = client.post("/api/v1/auth/register", json={
        "email": "register@example.com",
        "full_name": "New Student",
        "password": "Password123!",
        "role": "student"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "register@example.com"
    assert data["role"] == "student"

def test_verify_email_otp(client):
    client.post("/api/v1/auth/register", json={
        "email": "otpuser@example.com",
        "full_name": "OTP User",
        "password": "Password123!"
    })
    db = TestingSessionLocal()
    usr = db.query(User).filter(User.email == "otpuser@example.com").first()
    otp_code = usr.verification_code
    db.close()

    resp = client.post("/api/v1/auth/verify-email", json={
        "email": "otpuser@example.com",
        "code": otp_code
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_invalid_credentials(client):
    resp = client.post("/api/v1/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert resp.status_code == 400

def test_get_current_user_me(client):
    token = create_user_and_get_token(client, email="meuser@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "meuser@example.com"
