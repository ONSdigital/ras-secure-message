# ras-secure-message
[![Build Status](https://travis-ci.org/ONSdigital/ras-secure-message.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-secure-message) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4e427a826650454d98ed74dade65a4ff)](https://www.codacy.com/app/ONSDigital/ras-secure-message)
[![codecov](https://codecov.io/gh/ONSdigital/ras-secure-message/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-secure-message)


## Setup
Based on python 3.4

Create a virtual env for python3 and make sure that it's activated

```
mkvirtual --python=</path/to/python3.4 <your env name>
```

Install dependencies for the application using pip

```
pip install -r requirements.txt
```
The next step is to set the environment variables.
This can be done either by setting it in the terminal, in the IDE (PyCharm or whichever one is being used)
or by setting it in the source file. For example '.zshrc' '.bashrc' etc

```
export RAS_SM_PATH=/Users/user/projects/secure-messaging/ras-secure-message
```
```
SM_JWT_ENCRYPT = 1
SMS_LOG_LEVEL = DEBUG
```

Run the application
-------------------
```
$ python run.py
 * Running on http://127.0.0.1:5050/
 * Restarting with reloader
```

Test the application
--------------------
Install dependencies for the tests using pip

```
pip install -r requirements-test.txt
```
Once these have been installed the tests can be run from the ras-secure-message directory using the following
```
python run_tests.py
```

Test the response
-----------------

Now open up a prompt to test out your API using curl
```
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
| JWT_ALGORITHM                   | Algotithm used to code JWT                         | 'HS256'
| JWT_SECRET                      | SECRET used to code JWT                            | N/A
| SECURE_MESSAGING_DATABASE_URL   | Database URI                                       | sqlite:////tmp/messages.db
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