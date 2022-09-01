from pydantic import BaseModel

class AuthModel(BaseModel):
    username: str = ""
    password: str = ""

class UserModel(BaseModel):
    username: str
    org: str
    name: str
    admin: bool
    
class TicketModel(BaseModel):
    username: str
    org: str
    subject: str
    body: dict

class CommentModel(BaseModel):
    username: str
    body: dict
    org: str
    ticket: str

class TicketTags(BaseModel):
    tags: str
    ticketId: str

class AssignUser(BaseModel):
    ticket: str
    userid: str

class UpdateComment(BaseModel):
    body: dict
    commentId: str

class RegisterUser(UserModel):
    password: str
    adminCode: str

class CustomSQL(BaseModel):
    query: str

