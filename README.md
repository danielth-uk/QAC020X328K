
# Software Engineering and Agile


*Created By Daniel Thompson*

[![Push Master](https://github.com/danielth-uk/QAC020X328K/actions/workflows/push_master.yaml/badge.svg?branch=master)](https://github.com/danielth-uk/QAC020X328K/actions/workflows/push_master.yaml)

<hr/>


## Requirements

- Python3.7
- MySQL server
- Docker

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

# To Use 

## Starting Local Prod Env

To get started running the whole setup with one command, you must have docker and docker-compose installed (docker now has a form of compose built in, to check run `docker compose --help`). Then you can go to [https://localhost/](https://localhost/) to see the app.

```
> docker-compose up --build
```


## Dev

### Installing dependencies

To install dependencies run the following command in the root directory (where requirements.txt is)

```powershell
> pip install -r requirements.txt
```


### Powershell

This must be run in the `app` directory
``` powershell
> $PYTHONPATH=$PWD; $env:ENV="DEV"; uvicorn main:app --port 443
```

## Testing

``` powershell
> $PYTHONPATH=$PWD; python -m pytest
```

## Linting
```
> flake8
```

<br />

# Containerising it

Note you must have a `.local.env` file with the following ENV Params in the root directory

```ENV
ENV=DEV
JWT_SECRET=
DATABASE_DB=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
```

*You must also change main.py to the production implementation noted [Here](#dev)*

``` powershell
-- Building --
> docker build --tag backend .

-- Running --
> docker run --env-file .local.env -p 443:443 -d backend
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


CI/CD References
* https://docs.github.com/en/actions/publishing-packages/publishing-docker-images
* https://stackoverflow.com/questions/54310050/how-to-version-build-artifacts-using-github-actions
* https://github.com/marketplace/actions/create-or-update-release
* https://github.com/marketplace/actions/generate-version-tag
* https://github.com/marketplace/actions/changelog-release