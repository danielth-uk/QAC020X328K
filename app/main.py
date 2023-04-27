import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.responses import JSONResponse

from app.ApiModels import *
from app.functionsMain import *

from pathlib import Path
BASE_PATH = Path(__file__).resolve().parent

app = FastAPI()

# Enabling CORS to allow frontend to send requests to the backend
origins = [
    "http://localhost:3000",
    "http://localhost:8084",
    "http://localhost:8080",
    "http://localhost:8090",
]

# Allows requests from multiple origins and all methods
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"] 
)

# Setting the auth schema for requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Defines where the static web page files are located
app.mount("/static", StaticFiles(directory=str(BASE_PATH / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_PATH / "Templates"))


# Checks the bearer to see if its valid, and if the user is authorized for the request
def check_api_key(security_scopes: SecurityScopes, api_key: str = Depends(oauth2_scheme)):
    checkRequestAuth(api_key, security_scopes.scopes)


# Custom Error handler to return different errors
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"reason": exc.reason},
    )


# =======================================================================
#                          API Endpoints from here
#                               ANY Query
# =======================================================================

# For every authenticated required request, each endpoint will have an "AuthCheck" variable that is not read,
# but will require users to be authenticated and have the right authorization or a HTTPException will be raised
@app.post("/api/admin/danger", tags=["Admin Methods"])
async def admin_run_query(request: CustomSQL, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminRunCustomQuery(request)


# =======================================================================
#                          API Endpoints from here
#                             ADMIN endpoints
#
#      All of the endpoints below will run a different functions in the
#      main functions file.
# =======================================================================

# Returns a list of all the orgs in the database
@app.get("/api/admin/orgs", tags=["Admin Methods"])
def admin_get_orgs(AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminGetOrgs()


# Used to get different types of users from the DB (Admin or Client)
@app.get("/api/admin/users/{type}", tags=["Admin Methods"])
def admin_get_users(type: str, org: str = "", AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    if (type == "client"):
        return adminGetUserTypes(0, org)

    elif (type == "admin"):
        return adminGetUserTypes(1, org)

    else:
        raise HTTPException(status_code=404, detail="User type not valid")


@app.post("/api/admin/users/", tags=["Admin Methods"])
def admin_create_users(userDetails: UserModel, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return createUser(userDetails)


@app.put("/api/admin/users/{userId}", tags=["Admin Methods"])
def admin_update_user(userDetails: UserModel, userId: str, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return updateUser(userDetails, userId)


@app.delete("/api/admin/users/{userId}", tags=["Admin Methods"])
def admin_delete_user(userId: str, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return deleteUser(userId)


@app.post("/api/admin/pwdReset/{org}/{userId}", tags=["Admin Methods"])
def admin_reset_password(org: str, userId: str, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return resetPassword(org, userId)


@app.get("/api/admin/tickets", tags=["Admin Methods"])
def admin_get_tickets(AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminGetTickets()


@app.get("/api/admin/getAdmins", tags=["Admin Methods"])
def admin_get_admins(AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminGetAdmins()


@app.put("/api/admin/updateAdmin/{ticketId}", tags=["Admin Methods", "Ticket Methods"])
async def admin_update_assigned(ticketId: int, data: AssignUser, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminUpdateAssigned(ticketId, data)


@app.put("/api/admin/closeTicket/{ticketId}", tags=["Admin Methods"])
def admin_update_close_ticket(ticketId: int, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminCloseTicket(ticketId)


@app.delete("/api/admin/comment/{commentId}", tags=["Admin Methods"])
def admin_delete_comment(commentId: int, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminDeleteComment(commentId)


@app.put("/api/admin/tags/", tags=["Admin Methods"])
def admin_update_tags(data: TicketTags, AuthCheck: bool = Security(check_api_key, scopes=["Admin"])):
    return adminUpdateTags(data.ticketId, data.tags)

# =======================================================================
#                             CLIENT endpoints
# =======================================================================


@app.get("/api/client/tickets", tags=["Client Methods", "Ticket Methods"])
async def get_client_tickets(request: Request, org: bool, AuthCheck: bool = Security(check_api_key, scopes=["Client"])):
    return clientGetTickets(org, request.cookies["org"].lower(), request.cookies["username"].lower())


@app.post("/api/client/tickets", tags=["Client Methods", "Ticket Methods"])
def create_client_ticket(data: TicketModel, AuthCheck: bool = Security(check_api_key, scopes=["Client"])):
    return clientCreateTicket(data.username, data.org, data.subject, data.body)

# =======================================================================
#                             Ticket endpoints
# =======================================================================


@app.get("/api/general/tickets/{ticketId}", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def get_ticket_single_ticket(org: str, ticketId: int, AuthCheck: bool = Security(check_api_key, scopes=["Admin", "Client"])):
    return ticketOpenTicket(org, ticketId)


@app.get("/api/general/tickets/{ticketId}/comments", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def get_ticket_comments(ticketId: int, AuthCheck: bool = Security(check_api_key, scopes=["Client", "Admin"])):
    return ticketGetTicketComments(ticketId)


@app.post("/api/general/comments", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def create_ticket_comment(data: CommentModel, request: Request, AuthCheck: bool = Security(check_api_key, scopes=["Client", "Admin"])):
    # return ticketCreateTicketComment("qa","qa.admin", data)
    return ticketCreateTicketComment(request.cookies["org"].lower(), request.cookies["username"].lower(), data)


@app.put("/api/general/comments/{commentId}", tags=["Admin Methods", "Client Methods", "Ticket Methods"])
def update_ticket_comment(data: UpdateComment, commentId: int, AuthCheck: bool = Security(check_api_key, scopes=["Client", "Admin"])):
    return ticketUpdateComment(data, commentId)


# =======================================================================
#                             General endpoints
# =======================================================================

# Used to authenticated the user, must add database checks here
@app.post("/api/auth", tags=["General Methods"])
async def check_auth(credentials: AuthModel):
    return checkAuthentication(credentials.username, credentials.password)


@app.post("/api/register", tags=["General Methods"])
def register_user(details: RegisterUser):
    return registerUser(username=details.username, password=details.password, org=details.org, name=details.name, adminCode=details.adminCode)


# Used to send demo credentials to the login page for testing and assessment
@app.get("/api/auth/demo", tags=["General Methods"])
def get_demo_credentials():
    return getDemoUsers()


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
    # If there is a get request to an API endpoint that does not exist it will raise a 404
    if ("api" in str(request.url)):
        return templates.TemplateResponse("404.html", {"request": request})

    # If the page is at the root directory, it will send the page and the page will redirect to the correct URL
    if (str(request.url.path) == "/"):
        return templates.TemplateResponse("index.html", {"request": request})

    # Checks to see if there is a cookie called "Authorized"
    if ("Authorized" in request.cookies):
        # if the cookie exists and the requested url matches the contents of the cookie (either "admin" or "client")
        # it will return the page and not have to rely on client side page authorization otherwise will return 404
        if (request.cookies['Authorized'].lower() in str(request.url).lower()):
            return templates.TemplateResponse("index.html", {"request": request})
        else:
            return templates.TemplateResponse("404.html", {"request": request})

    # If there is no cookie, it will check to see if it is the login page, otherwise it will return 404
    else:
        return templates.TemplateResponse("index.html", {"request": request})


# Starts the API
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")


# https://pyjwt.readthedocs.io/en/latest/
# https://testdriven.io/tips/6840e037-4b8f-4354-a9af-6863fb1c69eb/
# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
# https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
# https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-6b-linode-deploy-gunicorn-uvicorn-nginx/
# https://docs.pytest.org/en/7.1.x/
# https://fastapi.tiangolo.com/tutorial/testing/
# https://fastapi.tiangolo.com/tutorial/handling-errors/
