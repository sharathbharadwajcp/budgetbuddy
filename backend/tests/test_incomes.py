import pytest
from tests.conftest import create_user_and_get_token

def test_income_crud(client):
    token = create_user_and_get_token(client, email="incomemodule@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Income
    resp = client.post("/api/v1/incomes/", headers=headers, json={
        "title": "Monthly Stipend",
        "amount": 1200.0,
        "category": "Stipend",
        "is_recurring": True
    })
    assert resp.status_code == 201
    inc_id = resp.json()["id"]

    # 2. List Incomes
    list_resp = client.get("/api/v1/incomes/", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["amount"] == 1200.0

    # 3. Delete Income
    del_resp = client.delete(f"/api/v1/incomes/{inc_id}", headers=headers)
    assert del_resp.status_code == 204
