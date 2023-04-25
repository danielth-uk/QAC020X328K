from fastapi.testclient import TestClient
import httpx
from app.main import app

client = TestClient(app)

# Used to get a new JWT on each test
def test_get_jwt():
    response = client.post("/api/auth",json={
        "username": "test.test",
        "password": "cGFzc3dvcmQ="
    })
    data = response.json()
    print("asd-asd-asd-asd-asd-asd")
    print(data)
    assert response.status_code == 200
    assert data
    return data["headers"]["jwt"]

# General Variables used throughout
varHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % test_get_jwt()
}

# Sets up cookies
varCookies = httpx.Cookies()
varCookies.set('org', 'test')
varCookies.set('username', 'Test')


# ================================================================
#                           Dangerous Test
# ================================================================

def test_client_get_tickets():
    response = client.get("/api/client/tickets?org=false", headers=varHeaders, cookies=varCookies)
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    assert response.json() == [] or response.json() == dict
