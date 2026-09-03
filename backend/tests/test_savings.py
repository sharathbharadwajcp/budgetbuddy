import pytest
from tests.conftest import create_user_and_get_token

def test_savings_goal_lifecycle(client):
    token = create_user_and_get_token(client, email="savingsmod@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Add Income $600
    client.post("/api/v1/incomes/", headers=headers, json={"title": "Salary", "amount": 600.0, "category": "Salary"})

    # Create Savings Goal
    goal_resp = client.post("/api/v1/savings/", headers=headers, json={
        "title": "Emergency Fund",
        "target_amount": 500.0,
        "current_amount": 0.0,
        "category": "General"
    })
    assert goal_resp.status_code == 201
    goal_id = goal_resp.json()["id"]

    # Deposit $250 (50% milestone achieved)
    dep_resp = client.post(f"/api/v1/savings/{goal_id}/deposit", headers=headers, json={"amount": 250.0})
    assert dep_resp.status_code == 200
    assert dep_resp.json()["current_amount"] == 250.0

    # Verify milestone notification created
    notif_resp = client.get("/api/v1/notifications/", headers=headers)
    assert notif_resp.status_code == 200
    assert len(notif_resp.json()) >= 1
