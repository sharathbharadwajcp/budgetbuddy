import pytest
from datetime import datetime
from tests.conftest import create_user_and_get_token

def test_create_and_list_expenses(client):
    token = create_user_and_get_token(client, email="expmodule@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Expense
    resp = client.post("/api/v1/expenses/", headers=headers, json={
        "title": "Textbooks",
        "amount": 85.50,
        "category": "Education",
        "payment_method": "Credit Card"
    })
    assert resp.status_code == 201
    exp_id = resp.json()["id"]

    # 2. List Expenses
    list_resp = client.get("/api/v1/expenses/", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["title"] == "Textbooks"

    # 3. Delete Expense
    del_resp = client.delete(f"/api/v1/expenses/{exp_id}", headers=headers)
    assert del_resp.status_code == 204

def test_expense_budget_overspend_trigger(client):
    token = create_user_and_get_token(client, email="overspend@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    current_month = datetime.utcnow().strftime("%Y-%m")

    # Set Budget of $100 for Food
    client.post("/api/v1/budgets/", headers=headers, json={
        "category": "Food",
        "amount_allocated": 100.0,
        "month": current_month
    })

    # Add Expense of $90 (90% spent) -> Triggers overspending alert
    exp_resp = client.post("/api/v1/expenses/", headers=headers, json={
        "title": "Fancy Dinner",
        "amount": 90.0,
        "category": "Food"
    })
    assert exp_resp.status_code == 201

    # Check notification generated
    notif_resp = client.get("/api/v1/notifications/", headers=headers)
    assert notif_resp.status_code == 200
    assert len(notif_resp.json()) >= 1
