from fastapi import HTTPException
import mysql.connector
import random, string, re,json, base64, jwt, os
from dotenv import load_dotenv

## TO Delete
# databasePassword = "sgMKT^wH297a0SMa"
# databaseUsername = "linroot"
# databaseHost = "lin-7936-5215-mysql-primary-private.servers.linodedb.net"
# JWTSecret="09d28166b70f4caa5e094faa6ca2556c816cf63b88e8da9563b93f7099f6f3e7"
# databasePassword = ""
# databaseUsername = "root"
# databaseHost = "localhost"


if(os.environ["ENV"] == "DEV"):
    load_dotenv()

JWTSecret=os.environ["JWT_SECRET"]
databasePassword = os.environ["DATABASE_PASSWORD"]
databaseUsername = os.environ["DATABASE_USER"]
databaseHost = os.environ["DATABASE_HOST"]
databaseDb = os.environ["DATABASE_DB"]

class UnicornException(Exception):
    def __init__(self, reason: str, status_code: int = 500):
        self.reason = reason
        self.status_code = status_code

# =======================================================================
#                             General functions
# =======================================================================

def checkRequestAuth(key, scopes):
    # Checks to see if there is a token in the database
    exists = databaseFetch("SELECT token FROM tbl_users WHERE token = '%s' " % (key))
    if(len(exists) == 0):
        raise HTTPException(status_code=403,detail="Forbidden")

    # Decodes the JWT and checks the authorization level and its in the scope of the request
    auth = jwt.decode(key, JWTSecret, algorithms="HS256")["Authorization"]
    if(auth not in scopes):
        raise HTTPException(status_code=403,detail="Forbidden, Unauthorized") 


# Cleans data so it can be stored in database (specifically newline from QuillJS)
def ticketBodyNormalize(data: dict, direction: bool) -> dict:
    # Checks to see if the dictionary is correct (coming from QuillJS)
    if("ops" in data):
        tempData = data["ops"]
    else:
        return HTTPException(status_code=500, detail="Dictionary not in required format")

    # Loops through all item attributes
    for item in tempData:
        if("insert" in item):
            if(direction):
                # Replaces \n with \\n for MySQL
                item["insert"] = re.sub(r'(\n+)', "\\\\n", item["insert"])
            else:
                item["insert"] = re.sub(r'(\\n+)', '\\n', item["insert"])
        
    return tempData
    
# A function used to open, retrieve and close database connection in once place
def databaseFetch(query: str) -> list:
    """ 
    Retrieves data from the database.
    Arguments:
        query: the SQL string to be executed
    Returns:
        list of results
     """
    # Will need to change credentials for env
    databaseConnection = mysql.connector.connect(
        host=databaseHost,
        user=databaseUsername,
        password=databasePassword,
        database=databaseDb
    )
    cursor = databaseConnection.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def databaseExecute(queryStatement: str, values: list = []) -> None:
    """ 
    Runs any non fetch query in the database.
    Arguments:
        queryStatement: the string query using %s for value placements
        values: a list of values to replace the %s in the query
    Returns:
        None
     """
    # Will need to change credentials for env
    databaseConnection = mysql.connector.connect(
        host=databaseHost,
        user=databaseUsername,
        password=databasePassword,
        database=databaseDb
    )
    cursor = databaseConnection.cursor()
    if(values == []):
        cursor.execute(queryStatement)
    else:
        cursor.execute(queryStatement, values)
    databaseConnection.commit()
    cursor.close()

# Used for credentials for demo purposes
def getDemoUsers() -> dict:
    # Selects all data and stores in var
    clientResult = databaseFetch("SELECT * FROM tbl_users WHERE admin = 0")
    adminResult = databaseFetch("SELECT * FROM tbl_users WHERE admin = 1")
    # uses random function to get a random one in the lists
    chosenAdmin = adminResult[random.randint(0,len(adminResult) - 1)]
    chosenClient = clientResult[random.randint(0,len(clientResult) - 1)]
    # Then returns picked users
    return {"admin" : {"username" : chosenAdmin["userid"], "password": chosenAdmin["password"]}, "client": {"username" : chosenClient["userid"], "password": chosenClient["password"]} }

# Checks authentication using username and password
def checkAuthentication(username: str, password: str) -> list:
    if(username == "" or password == ""): 
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    result = databaseFetch("SELECT * FROM tbl_users WHERE userid = '%s' AND password = '%s';" % (username, password))
    # return result
    if(len(result) == 0 or len(result) > 1):
        raise HTTPException(status_code=403, detail="Unauthenticated")
    else:
        # Checks to see if the user is an admin then will return data to the frontend
        if(result[0]["admin"]): 
            # Creates a JWT and uploads it into the database on sign in
            adminJWT = jwt.encode({"Authenticated": True, "Authorization": "Admin", "org": result[0]["org"].capitalize(), "name": result[0]["name"]}, JWTSecret, algorithm="HS256")
            databaseExecute("UPDATE tbl_users SET token=%s WHERE userid = %s", [adminJWT,  result[0]["org"] + "." + result[0]["username"]])
            return HTTPException(status_code=200, detail="Authenticated", headers={"jwt": adminJWT,"Authenticated": True, "Authorization": "Admin", "org": result[0]["org"].capitalize(), "name": result[0]["name"]})
            
            # return {"Authenticated": True, "Authorization": "Admin", "org": result[0]["org"].capitalize(), "name": result[0]["name"]}
        else:
            userJWT = jwt.encode({"Authenticated": True, "Authorization": "Client", "org": result[0]["org"].capitalize(), "name": result[0]["name"]}, JWTSecret, algorithm="HS256")
            databaseExecute("UPDATE tbl_users SET token=%s WHERE userid = %s", [userJWT,  result[0]["org"] + "." + result[0]["username"]])
            return HTTPException(status_code=200, detail="Authenticated", headers={"jwt": userJWT,"Authenticated": True, "Authorization": "Client", "org": result[0]["org"].capitalize(), "name": result[0]["name"]})
            # return {"jwt": userJWT,"Authenticated": True, "Authorization": "Client", "org": result[0]["org"].capitalize(), "name": result[0]["name"]}

def registerUser(username: str, password: str, org: str, name:str, adminCode: str) -> HTTPException:
    admin = False
    if(adminCode != ""):
        if(adminCode == "123456789"):
            admin = True
        else:
            raise UnicornException(status_code=403, reason="incorrect admin code")

    exists = databaseFetch("SELECT username FROM tbl_users WHERE userid = '%s' " % (org + "." + username))
    if(len(exists) > 0):
        raise UnicornException(status_code=409, reason="Username and org combination already exists")

    try:
        databaseExecute("INSERT INTO `tbl_users` VALUES (%s,%s,%s,%s,%s,%s,'')", [org.lower() + "." + username, org.lower(), username, password, admin, name])
        return HTTPException(status_code=201, detail="User Successfully Created", headers={"success": True, "reason": "User Created"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error", headers={"success": False, "reason": e})


# =======================================================================
#                             Admin functions
# =======================================================================

def adminGetUserTypes(type: str, org: str) -> list:
    if(org != ""): userResults = databaseFetch("SELECT userid, org, username,name FROM tbl_users WHERE admin = %s AND org = '%s'" % (type, org))
    else: userResults = databaseFetch("SELECT userid, org, username,name FROM tbl_users WHERE admin = %s" % type)
    return userResults

def adminGetOrgs() -> list:
    return databaseFetch("SELECT DISTINCT org FROM tbl_users")

def createUser(userDetails) -> HTTPException:
    exists = databaseFetch("SELECT username FROM tbl_users WHERE userid = '%s' " % (userDetails.org + "." + userDetails.username))
    if(len(exists) > 0):
        raise HTTPException(status_code=500, detail="Username and org combination already exists", headers={"success": False, "reason": "userid already exists"})
    else:
        password = ''.join(random.choice(string.ascii_uppercase) for i in range(16))
        
        databaseExecute("INSERT INTO `tbl_users` VALUES (%s,%s,%s,%s,%s,%s,'')", [userDetails.org + "." + userDetails.username, userDetails.org, userDetails.username, base64.b64encode(password.encode('ascii')).decode("utf-8"), userDetails.admin, userDetails.name])
        return HTTPException(status_code=201, detail="User Successfully created", headers={"success": True, "password": password})

def deleteUser(userId: str) -> None:
    databaseExecute("DELETE FROM tbl_users WHERE userid =%s", [userId])

def updateUser(details: str, userId: str) -> None:
    exists = databaseFetch("SELECT username FROM tbl_users WHERE userid = '%s' " % (details.org + "." + details.username))
    if(len(exists) > 0):
        raise HTTPException(status_code=500, detail="Username and org combination already exists", headers={"success": False, "reason": "userid already exists"})
    else:
        databaseExecute("UPDATE tbl_users SET userid=%s, username=%s,name=%s WHERE userid = %s", [details.org + "." + details.username, details.username, details.name, details.org + "." + userId])
        return HTTPException(status_code=201, detail="User Successfully created", headers={"success": True})

def resetPassword(org: str, userId: str) -> str:
    password = ''.join(random.choice(string.ascii_uppercase) for i in range(16))
    databaseExecute("UPDATE tbl_users SET password=%s WHERE userid = %s", [base64.b64encode(password.encode('ascii')).decode("utf-8"), org + "." + userId])
    return HTTPException(status_code=201, detail="password reset", headers={"success": True, "password": password})

def adminGetTickets():
    return databaseFetch("SELECT t.*, u1.name AS created_name, u2.name AS assigned_name FROM tbl_tickets AS t INNER JOIN tbl_users AS u1 ON t.created_by = u1.userid LEFT JOIN tbl_users AS u2 ON t.assigned_contact = u2.userid ORDER BY t.opened_time DESC")
    
def adminGetAdmins():
    return databaseFetch("SELECT userid, name FROM `tbl_users` WHERE admin = 1")

def adminUpdateAssigned(ticket, data):
    databaseExecute("UPDATE `tbl_tickets` SET `assigned_contact`=%s WHERE id = %s", [data.userid, ticket])
    return HTTPException(status_code=201, detail="Assigned User")

def adminDeleteComment(id):
    try:
        databaseExecute("DELETE FROM tbl_ticket_comments WHERE id = %s ", [id])
        return HTTPException(status_code=201, detail="Comment Deleted", headers={"success": True})
    except:
        raise HTTPException(status_code=500, detail="Cannot Delete Comment")

def adminCloseTicket(id):
    try:
        databaseExecute("UPDATE tbl_tickets SET closed=1 WHERE id = %s ", [id])
        return HTTPException(status_code=201, detail="Ticket Updated", headers={"success": True})
    except:
        raise HTTPException(status_code=500, detail="Cannot close ticket")

def adminUpdateTags(id, tags):
    try:
        databaseExecute("UPDATE tbl_tickets SET tags=%s WHERE id = %s ", [tags, id])
        return HTTPException(status_code=201, detail="tags Updated", headers={"success": True})
    except:
        raise HTTPException(status_code=500, detail="Cannot update Tags")  

## Reluctantly adding this feature
def adminRunCustomQuery(query) -> HTTPException:
    try:
        if(query.query == "RESET"):
            ## TO BUILD
            return HTTPException(status_code=204, detail="Database Reset", headers={"status_code": 204})
        elif("SELECT" in query.query):
            results = databaseFetch(query.query)
            return HTTPException(status_code=200, detail="Success", headers={"status_code": 200, "data": results})
        else:
            databaseExecute(query.query)
            return HTTPException(status_code=204, detail="No return content", headers={"status_code": 204})
    except Exception as e:
        return HTTPException(status_code=500, detail="Internal Server Error", headers={"status_code": 500, "error": e})
        

def adminResetDatabase():
    pass
    
# =======================================================================
#                             CLIENT functions
# =======================================================================


def clientGetTickets(org: bool, orgName: str = "", username: str = "") -> dict:
    try:
        if(org):
            return databaseFetch("SELECT t.*, u1.name AS created_name, u2.name AS assigned_name FROM tbl_tickets AS t INNER JOIN tbl_users AS u1 ON t.created_by = u1.userid LEFT JOIN tbl_users AS u2 ON t.assigned_contact = u2.userid WHERE t.org =  '%s' " % orgName)
        else:
            return databaseFetch("SELECT t.*, u1.name AS created_name, u2.name AS assigned_name FROM tbl_tickets AS t INNER JOIN tbl_users AS u1 ON t.created_by = u1.userid LEFT JOIN tbl_users AS u2 ON t.assigned_contact = u2.userid WHERE t.created_by =  '%s'" % username)
            
    except:
        raise HTTPException(status_code=403, detail="Missing request cookies")

def clientCreateTicket(username, org, subject, body) -> HTTPException:
    databaseExecute("INSERT INTO `tbl_tickets`(`subject`, `created_by`,`org`, `main_body`) VALUES (%s,%s,%s,%s)", [subject, username, org, json.dumps(ticketBodyNormalize(body, True))])
    return HTTPException(status_code=201, detail="Ticket Created")


# =======================================================================
#                             TICKET functions
# =======================================================================

def ticketOpenTicket(org: str, ticketId: int) -> dict:
    if(org == "qa"):
        data = databaseFetch("SELECT t.*, u1.name AS created_name, u2.name AS assigned_name FROM tbl_tickets AS t INNER JOIN tbl_users AS u1 ON t.created_by = u1.userid LEFT JOIN tbl_users AS u2 ON t.assigned_contact = u2.userid WHERE  t.id = '%s'" % (ticketId))
    else:
        data = databaseFetch("SELECT t.*, u1.name AS created_name, u2.name AS assigned_name FROM tbl_tickets AS t INNER JOIN tbl_users AS u1 ON t.created_by = u1.userid LEFT JOIN tbl_users AS u2 ON t.assigned_contact = u2.userid WHERE t.org = '%s' AND t.id = '%s'" % (org, ticketId))

    if(len(data) == 1):
        data[0]["main_body"] = ticketBodyNormalize({"ops": json.loads(data[0]["main_body"])}, False)
        return data[0]
    else:
        raise HTTPException(status_code=404, detail="Ticket Not Found")
    
def ticketGetTicketComments(ticketId):
    data = databaseFetch("SELECT id from tbl_tickets WHERE id = '%s'" % ticketId)
    if(len(data) == 1):
        data = databaseFetch("SELECT t.id, t.comment_body, t.posted_by, t.posted, t.updated, u1.name AS posted_name FROM tbl_ticket_comments AS t INNER JOIN tbl_users AS u1 ON t.posted_by = u1.userid WHERE ticket_id = '%s'" % ticketId)
        for comment in data:
            comment["comment_body"] = ticketBodyNormalize({"ops": json.loads(comment["comment_body"])},False)
        return data
    else:
        raise HTTPException(status_code=404, detail="Ticket Not Found")

def ticketCreateTicketComment(org, username, data):
    checkData = databaseFetch("SELECT id from tbl_tickets WHERE id = '%s'" % data.ticket)
    if(len(checkData) == 1):
        if(data.username == username and data.org == org):
            databaseExecute("INSERT INTO `tbl_ticket_comments`(`ticket_id`, `comment_body`, `posted_by`) VALUES (%s,%s,%s)", [data.ticket, json.dumps(ticketBodyNormalize(data.body, True)), data.username])
            return HTTPException(status_code=201, detail="Comment Created")
        else:
            raise HTTPException(status_code=403, detail="Authentication Error")
    else:
        raise HTTPException(status_code=404, detail="Ticket Not Found")
    
def ticketUpdateComment(data, commentId):
    databaseExecute("UPDATE `tbl_ticket_comments` SET `comment_body`=%s,`updated`= 1 WHERE id=%s", [json.dumps(ticketBodyNormalize(data.body, False)), commentId])
    return HTTPException(status_code=201, detail="Comment Updated")