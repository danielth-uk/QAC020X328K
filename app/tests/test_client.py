from fastapi.testclient import TestClient
import os, sys, httpx

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from main import app

client = TestClient(app)


# Used to get a new JWT on each test
def test_get_jwt():
    response = client.post(
        "/api/auth", json={"username": "test.user", "password": "cGFzc3dvcmQ="}
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

# Sets up cookies
varCookies = httpx.Cookies()
varCookies.set("org", "test")
varCookies.set("username", "Test")


# ================================================================
#                           Dangerous Test
# ================================================================


def test_client_get_tickets():
    response = client.get(
        "/api/client/tickets?org=false", headers=varHeaders, cookies=varCookies
    )
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    assert response.json() == dict
