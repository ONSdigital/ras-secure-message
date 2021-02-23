# ras-secure-message
[![Build Status](https://travis-ci.org/ONSdigital/ras-secure-message.svg?branch=main)](https://travis-ci.org/ONSdigital/ras-secure-message)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4e427a826650454d98ed74dade65a4ff)](https://www.codacy.com/app/ONSDigital/ras-secure-message)
[![codecov](https://codecov.io/gh/ONSdigital/ras-secure-message/branch/main/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-secure-message)


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
LOGGING_LEVEL = DEBUG
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
| LOGGING_LEVEL                   | Log level for the application                                 | 'DEBUG'
| SECURITY_USER_NAME              | Username for basic auth                                       | N/A
| SECURITY_USER_PASSWORD          | Password for basic auth                                       | N/A
| JWT_SECRET                      | SECRET used to code JWT                                       | N/A
| DATABASE_URL                    | Database URI                                                  | postgresql://postgres:postgres@localhost:5432
| NOTIFICATION_TEMPLATE_ID        | Template id for Gov Notify service                            | N/A
| NOTIFY_VIA_GOV_NOTIFY           | Toggle for using Gov Notify for notifications                 | '1' (enable Gov Notify email notifications)
| PARTY_URL                       | URL of the ras-party service                                  | N/A
| CLIENT_ID                       | ID of the client service in UAA                               | N/A
| CLIENT_SECRET                   | Password of the client service in UAA                         | N/A
| UAA_URL                         | URL of a UAA instance                                         | N/A
| USE_UAA                         | Sets whether a client token should be retrieved               | 1

## Database migrations

Although there exists a 'migrations' folder for SQL database migration files, this service does not currently use any database migration tools such as Alembic. As such, the migration files are simply there for record-keeping purposes. Migration scripts will need to be performed manually on the database.