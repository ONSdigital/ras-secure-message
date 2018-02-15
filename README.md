# ras-secure-message
[![Build Status](https://travis-ci.org/ONSdigital/ras-secure-message.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-secure-message)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4e427a826650454d98ed74dade65a4ff)](https://www.codacy.com/app/ONSDigital/ras-secure-message)
[![codecov](https://codecov.io/gh/ONSdigital/ras-secure-message/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-secure-message)


## Setup

[Install Docker](https://docs.docker.com/engine/installation/)

Install postgresql
```bash
brew install postgresql
```

Install pipenv
```bash
pip install pipenv
```

Use pipenv to create a virtualenv and install dependencies
```bash
pipenv install
```

Alternatively you can use make
```bash
make build
```

Set environmental variables. Replace $SOURCE_ROOT with the parent directory of the project.

```
RAS_SM_PATH=$SOURCE_ROOT/ras-secure-message
SM_JWT_ENCRYPT = 1
SMS_LOG_LEVEL = DEBUG
```

Run the application
-------------------
```bash
docker run -d -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -d postgres
pipenv run python run.py
 * Running on http://127.0.0.1:5050/
 * Restarting with reloader
```
or
```bash
docker-compose up
```
or (when postgres is set up)
```bash
make start
```


Test the application
--------------------
Ensure dev dependencies have been installed
```bash
pipenv install --dev
```

```bash
docker run -d -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -d postgres
pipenv run coverage run run_tests.py
```

Test the response
-----------------

Now open up a prompt to test out your API using curl
```bash
$ curl http://127.0.0.1:5050/health
{"status": "healthy"}
```

## Configuration

Environment variables available for configuration are listed below:

| Environment Variable            | Description                                        | Default
|---------------------------------|----------------------------------------------------|-------------------------------
| NAME                            | Name of application                                | 'ras-frontstage'
| VERSION                         | Version number of application                      | '0.1.0' (manually update as application updates)
| SECURITY_USER_NAME              | Username for basic auth                            | N/A
| SECURITY_USER_PASSWORD          | Password for basic auth                            | N/A
| JWT_ALGORITHM                   | Algorithm used to code JWT                         | 'HS256'
| JWT_SECRET                      | SECRET used to code JWT                            | N/A
| SECURE_MESSAGING_DATABASE_URL   | Database URI                                       | postgresql://postgres:postgres@localhost:5432
| NOTIFICATION_SERVICE_ID         | Service id to use Gov Notify service               | N/A
| NOTIFICATION_API_KEY            | API key to use Gov Notify service                  | N/A
| NOTIFICATION_TEMPLATE_ID        | Template id for Gov Notify service                 | N/A
| NOTIFY_VIA_GOV_NOTIFY           | Toggle for using Gov Notify for notifications      | '1' (enable Gov Notify email notifications)
| SM_JWT_ENCRYPT                  | Toggle to use encrypted tokens                     | '1' (enable encrypted tokens)
| NOTIFY_CASE_SERVICE             | Toggle to notify case service                      | '1' (enable notifying case service)

For each external application which frontstage communicates with there are 3 environment variables e.g. for the RM case service:

| Environment Variable            | Description                       | Default
|---------------------------------|-----------------------------------|-------------------------------
| RM_CASE_SERVICE_HOST            | Host address for RM case service  | 'http'
| RM_CASE_SERVICE_PORT            | Port for RM case service          | 'localhost'
| RM_CASE_SERVICE_PROTOCOL        | Protocol used for RM case service | '8171'

The services these variables exist for are listed below with the beginnings of their variables and their github links:

| Service                         | Start of variables          | Github
|---------------------------------|-----------------------------|-----------------------------
| Case service                    | RM_CASE_SERVICE             | https://github.com/ONSdigital/rm-case-service
| Party service                   | RAS_PARTY_SERVICE           | https://github.com/ONSdigital/ras-party
