import pytest
from app.models import User
from tests.conftest import create_user_and_get_token, TestingSessionLocal

def test_admin_dashboard_stats_and_role_restrictions(client):
    # Create Admin
    admin_token = create_user_and_get_token(client, email="adminmod@example.com", role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Create Student
    student_token = create_user_and_get_token(client, email="studentmod@example.com", role="student")

    db = TestingSessionLocal()
    admin_usr = db.query(User).filter(User.email == "adminmod@example.com").first()
    student_usr = db.query(User).filter(User.email == "studentmod@example.com").first()
    admin_id = admin_usr.id
    student_id = student_usr.id
    db.close()

    # 1. Admin Stats
    stats_resp = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert stats_resp.status_code == 200
    assert stats_resp.json()["user_statistics"]["total_users"] >= 2

    # 2. Block Admin from altering their own role (Returns 400)
    self_role_resp = client.put(f"/api/v1/admin/users/{admin_id}/role?role=student", headers=admin_headers)
    assert self_role_resp.status_code == 400
    assert "cannot alter their own" in self_role_resp.json()["detail"]

    # 3. Block promoting other user to admin (Returns 400)
    promote_resp = client.put(f"/api/v1/admin/users/{student_id}/role?role=admin", headers=admin_headers)
    assert promote_resp.status_code == 400
    assert "restricted" in promote_resp.json()["detail"]

    # 4. Valid upgrade student to premium
    upgrade_resp = client.put(f"/api/v1/admin/users/{student_id}/role?role=premium", headers=admin_headers)
    assert upgrade_resp.status_code == 200
    assert upgrade_resp.json()["role"] == "premium"
