import uvicorn
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import SecurityScopes, APIKeyHeader
from fastapi.responses import JSONResponse

import modules.ApiModels as models
import modules.functionsMain as functions

from pathlib import Path
BASE_PATH = Path(__file__).resolve().parent

app = FastAPI(docs_url=None, redoc_url=None)

# Enabling CORS to allow frontend to send requests to the backend
origins = [
    "https://localhost",
]

# Allows requests from multiple origins and all methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Forwards http requests to https (doesnt work in docker compose and Im not sure why)
app.add_middleware(HTTPSRedirectMiddleware)

# Setting the auth schema for requests
oauth2_scheme = APIKeyHeader(name='Authorization', auto_error=True)

# Defines where the static web page files are located
app.mount("/static", StaticFiles(directory=str(BASE_PATH / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_PATH / "Templates"))


# Checks the bearer to see if its valid, and if the user is authorized for the request
def check_api_key(security_scopes: SecurityScopes, api_key: str = Depends(oauth2_scheme)):
    functions.checkRequestAuth(api_key, security_scopes.scopes)


# Custom Error handler to return different errors
@app.exception_handler(functions.UnicornException)
async def unicorn_exception_handler(request: Request, exc: functions.UnicornException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"reason": exc.reason},
    )


# =======================================================================
#                          API Endpoints from here
#                               ANY Query
# =======================================================================

# For every authenticated required request, each endpoint will have an "auth_check" variable that is not read,
# but will require users to be authenticated and have the right authorization or a HTTPException will be raised
@app.post("/api/admin/danger", tags=["Admin Methods"])
async def admin_run_query(request: models.CustomSQL, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminRunCustomQuery(request)


# =======================================================================
#                          API Endpoints from here
#                             ADMIN endpoints
#
#      All of the endpoints below will run a different functions in the
#      main functions file.
# =======================================================================

# Returns a list of all the orgs in the database
@app.get("/api/admin/orgs", tags=["Admin Methods"])
def admin_get_orgs(auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminGetOrgs()


# Used to get different types of users from the DB (Admin or Client)
@app.get("/api/admin/users/{type}", tags=["Admin Methods"])
def admin_get_users(type: str, org: str = "", auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    if (type == "client"):
        return functions.adminGetUserTypes(0, org)

    elif (type == "admin"):
        return functions.adminGetUserTypes(1, org)

    else:
        raise HTTPException(status_code=404, detail="User type not valid")


@app.post("/api/admin/users/", tags=["Admin Methods"])
def admin_create_users(user_details: models.UserModel, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.createUser(user_details)


@app.put("/api/admin/users/{user_id}", tags=["Admin Methods"])
def admin_update_user(user_details: models.UserModel, user_id: str, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.updateUser(user_details, user_id)


@app.delete("/api/admin/users/{user_id}", tags=["Admin Methods"])
def admin_delete_user(user_id: str, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.deleteUser(user_id)


@app.post("/api/admin/pwdReset/{org}/{user_id}", tags=["Admin Methods"])
def admin_reset_password(org: str, user_id: str, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.resetPassword(org, user_id)


@app.get("/api/admin/tickets", tags=["Admin Methods"])
def admin_get_tickets(auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminGetTickets()


@app.get("/api/admin/getAdmins", tags=["Admin Methods"])
def admin_get_admins(auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminGetAdmins()


@app.put("/api/admin/updateAdmin/{ticket_id}", tags=["Admin Methods", "Ticket Methods"])
async def admin_update_assigned(ticket_id: int, data: models.AssignUser, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminUpdateAssigned(ticket_id, data)


@app.put("/api/admin/closeTicket/{ticket_id}", tags=["Admin Methods"])
def admin_update_close_ticket(ticket_id: int, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminCloseTicket(ticket_id)


@app.delete("/api/admin/comment/{comment_id}", tags=["Admin Methods"])
def admin_delete_comment(comment_id: int, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminDeleteComment(comment_id)


@app.put("/api/admin/tags/", tags=["Admin Methods"])
def admin_update_tags(data: models.TicketTags, auth_check: bool = Security(check_api_key, scopes=["Admin"])):
    return functions.adminUpdateTags(data.ticketId, data.tags)

# =======================================================================
#                             CLIENT endpoints
# =======================================================================


@app.get("/api/client/tickets", tags=["Client Methods", "Ticket Methods"])
async def get_client_tickets(request: Request, org: bool, auth_check: bool = Security(check_api_key, scopes=["Client"])):
    user_details = functions.getUserDetailsFromJwt(request.headers.get('authorization'))
    return functions.clientGetTickets(org, user_details["org"].lower(), user_details["userid"].lower())


@app.post("/api/client/tickets", tags=["Client Methods", "Ticket Methods"])
def create_client_ticket(data: models.TicketModel, auth_check: bool = Security(check_api_key, scopes=["Client"])):
    return functions.clientCreateTicket(data.username, data.org, data.subject, data.body)

# =======================================================================
#                             Ticket endpoints
# =======================================================================


@app.get("/api/general/tickets/{ticket_id}", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def get_ticket_single_ticket(org: str, ticket_id: int, auth_check: bool = Security(check_api_key, scopes=["Admin", "Client"])):
    return functions.ticketOpenTicket(org, ticket_id)


@app.get("/api/general/tickets/{ticket_id}/comments", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def get_ticket_comments(ticket_id: int, auth_check: bool = Security(check_api_key, scopes=["Client", "Admin"])):
    return functions.ticketGetTicketComments(ticket_id)


@app.post("/api/general/comments", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def create_ticket_comment(data: models.CommentModel, request: Request, auth_check: bool = Security(check_api_key, scopes=["Client", "Admin"])):
    user_details = functions.getUserDetailsFromJwt(request.headers.get('authorization'))
    return functions.ticketCreateTicketComment(user_details["org"].lower(), user_details["userid"].lower(), data)


@app.put("/api/general/comments/{comment_id}", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def update_ticket_comment(data: models.UpdateComment, comment_id: int, auth_check: bool = Security(check_api_key, scopes=["Client", "Admin"])):
    return functions.ticketUpdateComment(data, comment_id)


# =======================================================================
#                             General endpoints
# =======================================================================

# Used to authenticated the user, must add database checks here
@app.post("/api/auth", tags=["General Methods"])
async def check_auth(credentials: models.AuthModel):
    return functions.checkAuthentication(credentials.username, credentials.password)


@app.post("/api/register", tags=["General Methods"])
def register_user(details: models.RegisterUser):
    return functions.registerUser(username=details.username, password=details.password, org=details.org, name=details.name, adminCode=details.adminCode)


# Used to send demo credentials to the login page for testing and assessment
@app.get("/api/auth/demo", tags=["General Methods"])
def get_demo_credentials():
    return functions.getDemoUsers()


# =======================================================================
#                          End of API endpoints
#                 Sending frontend data and validating auth
# =======================================================================


# Any path other than those previously defined will send the main web page and
# further routing is handled on the client-side using React
@app.get("/{full_path:path}", tags=["General Methods"])
async def serves_webapp(request: Request):
    """
    # Webpage Serve Endpoint
    `/`
    - if any route, it will return React Frontend
    - Will also check the cookie `Authorized` to see if it is valid when going to authorized areas, such as `/Admin` or `/Client`, if not authorized, will return 404

    <br />

    `/api`
    - Returns 404 page, if it is not defined above, and it does not exist

    """
    user_details = functions.getUserDetailsFromJwt(request.headers.get('authorization'))

    index_page_template = templates.TemplateResponse("index.html", {"request": request})
    not_found_page_template = templates.TemplateResponse("404.html", {"request": request})

    # If there is a get request to an API endpoint that does not exist it will raise a 404
    if ("api" in str(request.url)):
        return not_found_page_template

    # If the page is at the root directory, it will send the page and the page will redirect to the correct URL
    if (str(request.url.path) == "/"):
        return index_page_template

    # Checks to see if they are authorized
    if ("Authenticated" in user_details):
        if (user_details["Authorization"] in str(request.url).lower()):
            return index_page_template
        else:
            return not_found_page_template

    # If there is no cookie, it will check to see if it is the login page, otherwise it will return 404
    else:
        return index_page_template


# Starts the API
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=443,
        ssl_keyfile="./static/ssl/localhost.decrypted.key",
        ssl_certfile="./static/ssl/localhost.crt"
    )


# https://pyjwt.readthedocs.io/en/latest/
# https://testdriven.io/tips/6840e037-4b8f-4354-a9af-6863fb1c69eb/
# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
# https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
# https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-6b-linode-deploy-gunicorn-uvicorn-nginx/
# https://docs.pytest.org/en/7.1.x/
# https://fastapi.tiangolo.com/tutorial/testing/
# https://fastapi.tiangolo.com/tutorial/handling-errors/
