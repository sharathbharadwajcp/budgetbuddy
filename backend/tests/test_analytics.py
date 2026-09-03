import pytest
from tests.conftest import create_user_and_get_token

def test_analytics_summary_and_trends(client):
    token = create_user_and_get_token(client, email="analyticsmod@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/incomes/", headers=headers, json={"title": "Allowance", "amount": 1000.0, "category": "General"})
    client.post("/api/v1/expenses/", headers=headers, json={"title": "Rent", "amount": 400.0, "category": "Housing"})

    # Summary
    sum_resp = client.get("/api/v1/analytics/summary", headers=headers)
    assert sum_resp.status_code == 200
    assert sum_resp.json()["total_income"] == 1000.0
    assert sum_resp.json()["total_expense"] == 400.0

    # Categories
    cat_resp = client.get("/api/v1/analytics/categories", headers=headers)
    assert cat_resp.status_code == 200
    assert len(cat_resp.json()) == 1
    assert cat_resp.json()[0]["category"] == "Housing"

    # Trends
    trend_resp = client.get("/api/v1/analytics/trends?months_count=6", headers=headers)
    assert trend_resp.status_code == 200
    assert len(trend_resp.json()) == 6
