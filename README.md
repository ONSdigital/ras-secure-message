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
make build
```

Ensure there is a postgres instance running on port 5432
```bash
docker run -d -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres -d postgres
```

Run the tests with make
```bash
make test # Runs linters, behave and unit tests
make lint # Runs linters only
```
*Note: Ensure APP_SETTINGS isn't set in .env as it could cause the tests to fail
in a non obvious way.*


Run the behave tests with:
```bash
pipenv run behave # Runs all of the tests
pipenv run behave tests/behavioural/features/thread_get.feature # Runs individual feature test
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

| Environment Variable            | Description                                                   | Default
|---------------------------------|---------------------------------------------------------------|-------------------------------
| SMS_LOG_LEVEL                   | Log level for the application                                 | 'DEBUG'
| SECURITY_USER_NAME              | Username for basic auth                                       | N/A
| SECURITY_USER_PASSWORD          | Password for basic auth                                       | N/A
| JWT_ALGORITHM                   | Algorithm used to code JWT                                    | 'HS256'
| JWT_SECRET                      | SECRET used to code JWT                                       | N/A
| SECURE_MESSAGING_DATABASE_URL   | Database URI                                                  | postgresql://postgres:postgres@localhost:5432
| NOTIFICATION_TEMPLATE_ID        | Template id for Gov Notify service                            | N/A
| NOTIFY_VIA_GOV_NOTIFY           | Toggle for using Gov Notify for notifications                 | '1' (enable Gov Notify email notifications)
| CLIENT_ID                       | ID of the client service in UAA                               | N/A
| CLIENT_SECRET                   | Password of the client service in UAA                         | N/A
| UAA_URL                         | URL of a UAA instance                                         | N/A
| USE_UAA                         | Sets whether a client token should be retrieved               | 1

For each external application which secure-message communicates with there are 3 environment variables e.g. for the RAS Party service:

| Environment Variable              | Description                         | Default
|-----------------------------------|-------------------------------------|-------------------------------
| PARTY_SERVICE_HOST            | Host address for RAS party service  | 'http'
| PARTY_SERVICE_PORT            | Port for RAS party service          | 'localhost'
| PARTY_SERVICE_PROTOCOL        | Protocol used for RAS party service | '8081'

The services these variables exist for are listed below with the beginnings of their variables and their github links:

| Service                         | Start of variables          | Github
|---------------------------------|-----------------------------|-----------------------------
| Party service                   | PARTY_SERVICE           | https://github.com/ONSdigital/ras-party
