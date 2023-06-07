import os, sys, httpx
from fastapi.testclient import TestClient

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from app import main

client = TestClient(main.app)


def test_get_jwt_admin():
    response = client.post(
        "/api/auth", json={"username":  "test.admin", "password":  "cGFzc3dvcmQ="}
    )
    data = response.json()
    assert response.status_code == 200
    assert data
    return data["headers"]["jwt"]


def test_get_jwt_client():
    response = client.post(
        "/api/auth", json={"username":  "test.user", "password":  "cGFzc3dvcmQ="}
    )
    data = response.json()
    assert response.status_code == 200
    assert data
    return data["headers"]["jwt"]


varCookies = httpx.Cookies()
varCookies.set("org", "test")
varCookies.set("username", "Test")


varHeadersAdmin = {
    "Content-Type": "application/json",
    "Authorization": test_get_jwt_admin(),
}
varHeadersClient = {
    "Content-Type": "application/json",
    "Authorization": test_get_jwt_client(),
}

def test_admin_run_query_api_admin_danger_post_successful_response():
    response = client.post("/api/admin/danger", headers=varHeadersAdmin, json={"query": "string"})
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_run_query_api_admin_danger_post_successful_response():
    response = client.post("/api/admin/danger", json={"query": "string"})
    assert response.json()
    assert response.status_code == 403


def test_admin_run_query_api_admin_danger_post_validation_error():
    response = client.post("/api/admin/danger", headers=varHeadersAdmin, json={})
    assert response.json()
    assert response.status_code == 422


def test_no_authadmin_run_query_api_admin_danger_post_validation_error():
    response = client.post("/api/admin/danger", json={"query": "string"})
    assert response.json()
    assert response.status_code == 403


def test_admin_get_orgs_api_admin_orgs_get_successful_response():
    response = client.get("/api/admin/orgs", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_get_orgs_api_admin_orgs_get_successful_response():
    response = client.get("/api/admin/orgs")
    assert response.json()
    assert response.status_code == 403


def test_admin_get_users_api_admin_users__type__get_successful_response():
    response = client.get("/api/admin/users/admin", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_get_users_api_admin_users__type__get_successful_response():
    response = client.get("/api/admin/users/admin")
    assert response.json()
    assert response.status_code == 403


def test_admin_get_users_api_admin_users__type__get_not_founf():
    response = client.get("/api/admin/users/123", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 404


def test_no_authadmin_get_users_api_admin_users__type__get_validation_error():
    response = client.get("/api/admin/users/admin")
    assert response.json()
    assert response.status_code == 403


def test_no_authadmin_create_users_api_admin_users__post_successful_response():
    response = client.post("/api/admin/users/", json={"username": "string", "org": "string", "name": "string", "admin": 0})
    assert response.json()
    assert response.status_code == 403


def test_admin_create_users_api_admin_users__post_validation_error():
    response = client.post("/api/admin/users/", headers=varHeadersAdmin, json={"username": "string"})
    assert response.json()
    assert response.status_code == 422


def test_no_authadmin_create_users_api_admin_users__post_validation_error():
    response = client.post("/api/admin/users/", json={"username": "string", "org": "string", "name": "string", "admin": 0})
    assert response.json()
    assert response.status_code == 403


def test_no_authadmin_update_user_api_admin_users__userId__put_successful_response():
    response = client.put("/api/admin/users/test.user", json={"username": "string", "org": "string", "name": "string", "admin": 0})
    assert response.json()
    assert response.status_code == 403


def test_no_authadmin_update_user_api_admin_users__userId__put_validation_error():
    response = client.put("/api/admin/users/test.user", json={"username": "string", "org": "string", "name": "string", "admin": 0})
    assert response.json()
    assert response.status_code == 403


def test_admin_get_tickets_api_admin_tickets_get_successful_response():
    response = client.get("/api/admin/tickets", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_get_tickets_api_admin_tickets_get_successful_response():
    response = client.get("/api/admin/tickets")
    assert response.json()
    assert response.status_code == 403


def test_admin_get_admins_api_admin_getAdmins_get_successful_response():
    response = client.get("/api/admin/getAdmins", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_get_admins_api_admin_getAdmins_get_successful_response():
    response = client.get("/api/admin/getAdmins")
    assert response.json()
    assert response.status_code == 403


def test_no_authadmin_update_assigned_api_admin_updateAdmin__ticketId__put_successful_response():
    response = client.put("/api/admin/updateAdmin/1", json={"ticket": "1", "userid": "string"})
    assert response.json()
    assert response.status_code == 403

def test_admin_update_close_ticket_api_admin_closeTicket__ticketId__put_successful_response():
    response = client.put("/api/admin/closeTicket/1", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_update_close_ticket_api_admin_closeTicket__ticketId__put_successful_response():
    response = client.put("/api/admin/closeTicket/1")
    assert response.json()
    assert response.status_code == 403


def test_no_authadmin_update_close_ticket_api_admin_closeTicket__ticketId__put_validation_error():
    response = client.put("/api/admin/closeTicket/1")
    assert response.json()
    assert response.status_code == 403


def test_admin_delete_comment_api_admin_comment__commentId__delete_successful_response():
    response = client.delete("/api/admin/comment/1", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_delete_comment_api_admin_comment__commentId__delete_successful_response():
    response = client.delete("/api/admin/comment/1")
    assert response.json()
    assert response.status_code == 403


def test_no_authadmin_delete_comment_api_admin_comment__commentId__delete_validation_error():
    response = client.delete("/api/admin/comment/1")
    assert response.json()
    assert response.status_code == 403


def test_admin_update_tags_api_admin_tags__put_successful_response():
    response = client.put("/api/admin/tags/", headers=varHeadersAdmin, json={"tags": "string", "ticketId": "1"})
    assert response.json()
    assert response.status_code == 200


def test_no_authadmin_update_tags_api_admin_tags__put_successful_response():
    response = client.put("/api/admin/tags/", json={"tags": "string", "ticketId": "1"})
    assert response.json()
    assert response.status_code == 403


def test_no_authadmin_update_tags_api_admin_tags__put_validation_error():
    response = client.put("/api/admin/tags/", json={"tags": "string", "ticketId": "1"})
    assert response.json()
    assert response.status_code == 403


def test_no_authget_client_tickets_api_client_tickets_get_successful_response():
    response = client.get("/api/client/tickets")
    assert response.json()
    assert response.status_code == 403


def test_get_client_tickets_api_client_tickets_get_validation_error():
    response = client.get("/api/client/tickets", headers=varHeadersClient)
    assert response.json()
    assert response.status_code == 422


def test_no_authget_client_tickets_api_client_tickets_get_validation_error():
    response = client.get("/api/client/tickets")
    assert response.json()
    assert response.status_code == 403


def test_no_authcreate_client_ticket_api_client_tickets_post_successful_response():
    response = client.post("/api/client/tickets", json={"username": "string", "org": "string", "subject": "string", "body":{}})
    assert response.json()
    assert response.status_code == 403


def test_no_authget_ticket_single_ticket_api_general_tickets__ticketId__get_successful_response():
    response = client.get("/api/general/tickets/1")
    assert response.json()
    assert response.status_code == 403


def test_client_get_ticket_single_ticket_api_general_tickets__ticketId__get_validation_error():
    response = client.get("/api/general/tickets/1", headers=varHeadersClient)
    assert response.json()
    assert response.status_code == 422


def test_admin_get_ticket_single_ticket_api_general_tickets__ticketId__get_validation_error():
    response = client.get("/api/general/tickets/1", headers=varHeadersAdmin)
    assert response.json()
    assert response.status_code == 422


def test_no_authget_ticket_single_ticket_api_general_tickets__ticketId__get_validation_error():
    response = client.get("/api/general/tickets/1")
    assert response.json()
    assert response.status_code == 403


def test_no_authget_ticket_comments_api_general_tickets__ticketId__comments_get_successful_response():
    response = client.get("/api/general/tickets/1/comments")
    assert response.json()
    assert response.status_code == 403


def test_no_authget_ticket_comments_api_general_tickets__ticketId__comments_get_validation_error():
    response = client.get("/api/general/tickets/1/comments")
    assert response.json()
    assert response.status_code == 403


def test_no_authcreate_ticket_comment_api_general_comments_post_successful_response():
    response = client.post("/api/general/comments", json={"username": "string", "body":{},"org": "string", "ticket": "1"})
    assert response.json()
    assert response.status_code == 403


def test_client_create_ticket_comment_api_general_comments_post_validation_error():
    response = client.post("/api/general/comments", headers=varHeadersClient, json={"body":{},"org": "string", "ticket": "1"})   
    assert response.json()
    assert response.status_code == 422


def test_admin_create_ticket_comment_api_general_comments_post_validation_error():
    response = client.post("/api/general/comments", headers=varHeadersAdmin, json={"body":{},"org": "string", "ticket": "1"})    
    assert response.json()
    assert response.status_code == 422


def test_no_authupdate_ticket_comment_api_general_comments__commentId__put_validation_error():
    response = client.put("/api/general/comments/1", json={"body":{},"commentId": "string"})
    assert response.json()
    assert response.status_code == 403


def test_get_demo_credentials_api_auth_demo_get_successful_response():
    response = client.get("/api/auth/demo")
    assert response.json()
    assert response.status_code == 200
