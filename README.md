
# Software Engineering and Agile

*Created By Daniel Thompson*

[![Push Master](https://github.com/danielth-uk/QAC020X328K/actions/workflows/push_master.yaml/badge.svg?branch=master)](https://github.com/danielth-uk/QAC020X328K/actions/workflows/push_master.yaml)

<hr/>


## Requirements

- Python3.7
- nginx (for deployment)
- mySQL server

<br />

### Python Packages 
- pyjwt
- fastapi
- uvicorn
- mysql-connector-python

<br />

# The Application


This application uses serving HTML, JS and CSS to enable the frontend, the frontend has been built using ReactJS to create a smoother and more accessible feel in addition to providing client-side routing. This application is a basic ticketing solutions, with two different types of users that must be authenticated to use the application. Both the client-side JavaScript and the server side python application check auth with each request to ensure unauthenticated users cannot access API endpoints or pages.

Users can create, read and update their own tickets and comments, while admins can add, update, read and delete their own comments (as well as read all other comments per ticket). Admins can also close tickets and update ticket details such as assigned users and tags. Admin users also have the ability to create, delete and edit all users in the application as well as perform queries in the underlying database (not recommended to use)


<br />

# Deployment

This application has been deployed to X [To be added]. Using Nginx to reverse proxy incoming requests to the python application. [Tutorial Used Here](https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-6b-linode-deploy-gunicorn-uvicorn-nginx/)


# To use 

## Starting

### Powershell
``` powershell
> $env:ENV="DEV"; uvicorn app.main:app --reload
```

## Testing
```
> pytest
```

## Linting
```
> flake8
```

<br />

# Other
UI Frameworks used:
<br />
*https://daisyui.com/*  
*https://tailwindcss.com/*

<br />

General References
* https://pyjwt.readthedocs.io/en/latest/
* https://testdriven.io/tips/6840e037-4b8f-4354-a9af-6863fb1c69eb/
* https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
* https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
* https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-6b-linode-deploy-gunicorn-uvicorn-nginx/
* https://docs.pytest.org/en/7.1.x/
* https://fastapi.tiangolo.com/tutorial/testing/
* https://fastapi.tiangolo.com/tutorial/handling-errors/
