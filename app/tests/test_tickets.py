import os, sys, httpx

from fastapi.testclient import TestClient
from pytest_schema import schema
from response_schemas import TestSchemaTickets, TestSchmasGeneric

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from app import main

client = TestClient(main.app)
TicketSchema = TestSchemaTickets()
GenericSchemas = TestSchmasGeneric()


# Used to get a new JWT on each test
def test_get_jwt_admin():
    response = client.post(
        "/api/auth", json={"username": "test.admin", "password": "cGFzc3dvcmQ="}
    )
    data = response.json()
    assert response.status_code == 200
    assert data
    return data["headers"]["jwt"]


# Used to get a new JWT on each test
def test_get_jwt_client():
    response = client.post(
        "/api/auth", json={"username": "test.user", "password": "cGFzc3dvcmQ="}
    )
    data = response.json()
    assert response.status_code == 200
    assert data
    return data["headers"]["jwt"]


# General Variables used throughout
varHeadersAdmin = {
    "Content-Type": "application/json",
    "Authorization": test_get_jwt_admin(),
}
varHeadersClient = {
    "Content-Type": "application/json",
    "Authorization": test_get_jwt_client(),
}

# Sets up cookies
varCookies = httpx.Cookies()
varCookies.set("org", "test")
varCookies.set("username", "Test")


def test_get_admin_tickets_found():
    response = client.get(
        "/api/general/tickets/1?org=test", headers=varHeadersAdmin, cookies=varCookies
    )
    assert response.status_code == 200
    assert schema(TicketSchema.ticketGeneral) == response.json()


def test_get_client_tickets_found():
    response = client.get(
        "/api/general/tickets/1?org=test", headers=varHeadersClient, cookies=varCookies
    )
    assert response.status_code == 200
    assert schema(TicketSchema.ticketGeneral) == response.json()


def test_get_admin_tickets_not_found():
    response = client.get(
        "/api/general/tickets/2?org=test", headers=varHeadersAdmin, cookies=varCookies
    )
    assert response.status_code == 404
    assert schema(GenericSchemas.genericDetail) == response.json()
    assert response.json() == {"detail": "Ticket Not Found"}


def test_get_client_tickets_not_found():
    response = client.get(
        "/api/general/tickets/2?org=test", headers=varHeadersClient, cookies=varCookies
    )
    assert response.status_code == 404
    assert schema(GenericSchemas.genericDetail) == response.json()
    assert response.json() == {"detail": "Ticket Not Found"}


def test_get_admin_tickets_no_ticket():
    response = client.get(
        "/api/general/tickets/?org=test", headers=varHeadersAdmin, cookies=varCookies
    )
    assert response.status_code == 200


def test_get_client_tickets_no_ticket():
    response = client.get(
        "/api/general/tickets/?org=test", headers=varHeadersClient, cookies=varCookies
    )
    assert response.status_code == 200


def test_get_admin_tickets_no_org():
    response = client.get(
        "/api/general/tickets/1", headers=varHeadersAdmin, cookies=varCookies
    )
    assert response.status_code == 422
    assert schema(GenericSchemas.genericMissingParams) == response.json()


def test_get_client_tickets_no_org():
    response = client.get(
        "/api/general/tickets/1", headers=varHeadersClient, cookies=varCookies
    )
    assert response.status_code == 422
    assert schema(GenericSchemas.genericMissingParams) == response.json()


def test_get_admin_tickets_comments_found():
    response = client.get(
        "/api/general/tickets/1/comments", headers=varHeadersAdmin, cookies=varCookies
    )
    assert response.status_code == 200
    assert schema([TicketSchema.ticketComment]) == response.json()


def test_get_client_tickets_comment_found():
    response = client.get(
        "/api/general/tickets/1/comments", headers=varHeadersClient, cookies=varCookies
    )
    assert response.status_code == 200
    assert schema([TicketSchema.ticketComment]) == response.json()


def test_get_admin_tickets_comments_not_found():
    response = client.get(
        "/api/general/tickets/2/comments", headers=varHeadersAdmin, cookies=varCookies
    )
    assert response.status_code == 404
    assert schema(GenericSchemas.genericDetail) == response.json()
    assert response.json() == {"detail": "Ticket Not Found"}


def test_get_client_tickets_comment_not_found():
    response = client.get(
        "/api/general/tickets/2/comments", headers=varHeadersClient, cookies=varCookies
    )
    assert response.status_code == 404
    assert schema(GenericSchemas.genericDetail) == response.json()
    assert response.json() == {"detail": "Ticket Not Found"}


def test_get_admin_tickets_comments_not_int():
    response = client.get(
        "/api/general/tickets/a/comments", headers=varHeadersAdmin, cookies=varCookies
    )
    assert response.status_code == 422
    assert schema(GenericSchemas.genericMissingParams) == response.json()


def test_get_client_tickets_comment_not_int():
    response = client.get(
        "/api/general/tickets/a/comments", headers=varHeadersClient, cookies=varCookies
    )
    assert response.status_code == 422
    assert schema(GenericSchemas.genericMissingParams) == response.json()


def test_post_admin_new_comment_success():
    body = {
        "username": "test.admin",
        "body": [],
        "org": "test",
        "ticket": "1"
    }
    response = client.post(
        "/api/general/comments", headers=varHeadersClient, cookies=varCookies, json=body
    )
    assert response.status_code == 200


def test_post_client_new_comment_success():
    body = {
        "username": "test.user",
        "body": [],
        "org": "test",
        "ticket": "1"
    }
    response = client.post(
        "/api/general/comments", headers=varHeadersClient, cookies=varCookies, json=body
    )
    assert response.status_code == 200
