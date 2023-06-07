class TestSchmasGeneric:
    genericReason = {
        "reason": str
    }

    genericDetail = {
        "detail": str
    }

    genericMissingParams = {
        "detail": [
            {
                "loc": list,
                "msg": str,
                "type": str
            }
        ]
    }


class TestSchemasAuth:
    authDemo = {
        "admin": {
            "username": str,
            "password": str
        },
        "client": {
            "username": str,
            "password": str
        }
    }

    authLoginSuccess = {
        "status_code": int,
        "detail": str,
        "headers": {
            "jwt": str,
            "Authenticated": bool,
            "Authorization": str,
            "org": str,
            "name": str,
            "userid": str
        }
    }


class TestSchemaTickets:
    ticketGeneral = {
        "id": int,
        "subject": str,
        "created_by": str,
        "assigned_contact": str or None,
        "org": "test",
        "tags": str or None,
        "opened_time": str,
        "last_message": None,
        "main_body": dict,
        "closed": int,
        "created_name": str,
        "assigned_name": str or None
    }

    ticketComment = {
        "id": int,
        "comment_body": list,
        "posted_by": str,
        "posted": str,
        "updated": int,
        "posted_name": str
    }
