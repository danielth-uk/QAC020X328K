from fastapi.testclient import TestClient

import os, sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from app import main

client = TestClient(main.app)

# General Variables used throughout
varHeaders = {"Content-Type": "application/json"}


# ================================================================
#                           Demo Auth Test
# ================================================================
def test_demo_creds():
    response = client.get("/api/auth/demo")
    assert response.status_code == 200
    assert response.json()


# ================================================================
#                           Login Test
# ================================================================


# This does nothing other than return the response with specific
# credentials but defaults to no when running
def test_login_main(credentials: dict = {}):
    return client.post("/api/auth", json=credentials, headers=varHeaders)


def test_login_good_creds():
    response = test_login_main(
        {
            "username": "test.admin",
            "password": "cGFzc3dvcmQ="
        }
    )
    assert response.status_code == 200
    assert response.json()


def test_login_bad_creds():
    response = test_login_main(
        {
            "username": "qa.admin",
            "password": "password"
        }
    )
    assert response.status_code == 403


def test_login_no_creds():
    response = test_login_main({})
    assert response.status_code == 422


# ================================================================
#                       Registration Test
# ================================================================


def test_register_main(details: dict = {}):
    return client.post("/api/register", json=details, headers=varHeaders)


def test_register_existing_user():
    response = test_register_main(
        {
            "username": "admin",
            "org": "test",
            "name": "string",
            "admin": "true",
            "password": "string",
            "adminCode": "123456789",
        }
    )
    assert response.status_code == 409
    assert response.json() == {"reason": "Username and org combination already exists"}


def test_register_bad_admin_code():
    response = test_register_main(
        {
            "username": "string",
            "org": "string",
            "name": "string",
            "admin": "true",
            "password": "string",
            "adminCode": "string",
        }
    )
    assert response.status_code == 403
    assert response.json() == {"reason": "incorrect admin code"}


def test_register_no_creds():
    response = test_register_main({})
    assert response.status_code == 422


def test_register_user_good_creds():
    response = test_register_main(
        {
            "username": "admin",
            "org": "newtest",
            "name": "string",
            "admin": "false",
            "password": "ZEJNbCV4diNVfXskLEJQMQ==",
            "adminCode": "",
        }
    )
    assert response.status_code == 200
