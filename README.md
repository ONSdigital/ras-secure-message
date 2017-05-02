# ras-secure-message
[![Build Status](https://travis-ci.org/ONSdigital/ras-secure-message.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-secure-message) [![Code Issues](https://www.quantifiedcode.com/app/project/d02278acae1a498bae910f4eeac7c96f/badge.svg)](https://www.quantifiedcode.com/app/project/d02278acae1a498bae910f4eeac7c96f) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/94d065784ec14ed4aba8aeb4f36ce10a)](https://www.codacy.com/app/ONSDigital/ras-secure-message)
[![codecov](https://codecov.io/gh/ONSdigital/ras-secure-message/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-secure-message)


## Setup
Based on python 3.4

Create a new virtual env for python3

```
mkvirtual --python=</path/to/python3.4 <your env name>
```

Install dependencies using pip

```
pip install -r requirements.txt
```

Set RAS_SM_PATH environment variable

```
export RAS_SM_PATH=/Users/user/projects/secure-messaging/ras-secure-message
```

Run the application
-------------------
```
$ python run.py
 * Running on http://127.0.0.1:5000/
 * Restarting with reloader
```

Test the response
-----------------

Now open up a new prompt to test out your API using curl
```
$ curl http://127.0.0.1:5000/health
{"status": "healthy"}
```
