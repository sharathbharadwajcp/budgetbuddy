import pytest
from tests.conftest import create_user_and_get_token

def test_budget_creation_and_percent_used(client):
    token = create_user_and_get_token(client, email="budgetmodule@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Budget
    bud_resp = client.post("/api/v1/budgets/", headers=headers, json={
        "category": "Entertainment",
        "amount_allocated": 200.0
    })
    assert bud_resp.status_code == 201
    assert bud_resp.json()["amount_allocated"] == 200.0

    # 2. Add Expense under Entertainment of $50 (25% used)
    client.post("/api/v1/expenses/", headers=headers, json={
        "title": "Movie Tickets",
        "amount": 50.0,
        "category": "Entertainment"
    })

    # 3. Retrieve Budgets list & check computed total_spent and percent_used
    list_resp = client.get("/api/v1/budgets/", headers=headers)
    assert list_resp.status_code == 200
    bud = list_resp.json()[0]
    assert bud["total_spent"] == 50.0
    assert bud["percent_used"] == 25.0
