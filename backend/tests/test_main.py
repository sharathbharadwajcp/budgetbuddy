import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models import User

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
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def helper_create_and_verify_user(email, name, password):
    reg = client.post("/api/v1/auth/register", json={"email": email, "full_name": name, "password": password})
    db = TestingSessionLocal()
    usr = db.query(User).filter(User.email == email).first()
    otp = usr.verification_code
    db.close()
    
    ver = client.post("/api/v1/auth/verify-email", json={"email": email, "code": otp})
    return ver.json()["access_token"]

def test_register_and_login():
    # 1. Register User
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    assert reg_resp.status_code == 201
    assert reg_resp.json()["email"] == "testuser@example.com"

    # 2. Extract OTP & Verify
    db = TestingSessionLocal()
    usr = db.query(User).filter(User.email == "testuser@example.com").first()
    otp = usr.verification_code
    db.close()

    ver_resp = client.post("/api/v1/auth/verify-email", json={"email": "testuser@example.com", "code": otp})
    assert ver_resp.status_code == 200
    token = ver_resp.json()["access_token"]
    assert token is not None

def test_expense_crud():
    token = helper_create_and_verify_user("expuser@example.com", "Exp User", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Add Expense
    create_resp = client.post(
        "/api/v1/expenses/",
        headers=headers,
        json={"title": "Test Dinner", "amount": 45.0, "category": "Food", "payment_method": "Cash"}
    )
    assert create_resp.status_code == 201
    expense_id = create_resp.json()["id"]

    # List Expenses
    list_resp = client.get("/api/v1/expenses/", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Delete Expense
    del_resp = client.delete(f"/api/v1/expenses/{expense_id}", headers=headers)
    assert del_resp.status_code == 204

def test_cashflow_prediction():
    token = helper_create_and_verify_user("preduser@example.com", "Pred User", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Add Income & Expense
    client.post("/api/v1/incomes/", headers=headers, json={"title": "Allowance", "amount": 1000.0, "category": "Pocket Money"})
    client.post("/api/v1/expenses/", headers=headers, json={"title": "Groceries", "amount": 150.0, "category": "Food"})

    # Fetch prediction
    pred_resp = client.get("/api/v1/analytics/prediction", headers=headers)
    assert pred_resp.status_code == 200
    data = pred_resp.json()
    assert "daily_burn_rate" in data
    assert "projected_month_end_balance" in data
    assert "forecast_points" in data
    assert len(data["forecast_points"]) >= 28

def test_savings_deducted_from_income():
    token = helper_create_and_verify_user("savingsuser@example.com", "Savings User", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Add Income $500
    client.post("/api/v1/incomes/", headers=headers, json={"title": "Salary", "amount": 500.0, "category": "Salary"})

    # 2. Add Expense $100
    client.post("/api/v1/expenses/", headers=headers, json={"title": "Books", "amount": 100.0, "category": "Education"})

    # 3. Create Savings Goal
    goal_resp = client.post("/api/v1/savings/", headers=headers, json={
        "title": "Laptop Fund",
        "target_amount": 1000.0,
        "current_amount": 0.0,
        "category": "Tech"
    })
    goal_id = goal_resp.json()["id"]

    # 4. Try depositing $500 (Exceeds available $400) -> Should Fail with 400
    fail_dep = client.post(f"/api/v1/savings/{goal_id}/deposit", headers=headers, json={"amount": 500.0})
    assert fail_dep.status_code == 400
    assert "Insufficient available funds" in fail_dep.json()["detail"]

    # 5. Deposit $250 (Valid) -> Should Succeed
    succ_dep = client.post(f"/api/v1/savings/{goal_id}/deposit", headers=headers, json={"amount": 250.0})
    assert succ_dep.status_code == 200
    assert succ_dep.json()["current_amount"] == 250.0

    # 6. Verify Summary Analytics net_savings is now $150 ($500 income - $100 expense - $250 savings)
    sum_resp = client.get("/api/v1/analytics/summary", headers=headers)
    assert sum_resp.status_code == 200
    assert sum_resp.json()["net_savings"] == 150.0
