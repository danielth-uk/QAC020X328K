from fastapi.testclient import TestClient

import os, sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from main import app

client = TestClient(app)


# Used to get a new JWT on each test
def test_get_jwt():
    response = client.post(
        "/api/auth", json={
            "username": "test.admin",
            "password": "cGFzc3dvcmQ="
        }
    )
    data = response.json()
    assert response.status_code == 200
    assert data
    return data["headers"]["jwt"]


# General Variables used throughout
varHeaders = {
    "Content-Type": "application/json",
    "Authorization": test_get_jwt(),
}


# ================================================================
#                           Dangerous Test
# ================================================================


def test_admin_danger_authenticated():
    response = client.post(
        "/api/admin/danger",
        json={"query": "SELECT * FROM tbl_users"},
        headers=varHeaders,
    )
    assert response.status_code == 200
    assert response.json()


def test_admin_danger_no_auth():
    response = client.post(
        "/api/admin/danger", json={"query": "SELECT * FROM tbl_users"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
