# secure-messaging-api
[![Build Status](https://travis-ci.org/qateam123/secure-messaging-api.svg?branch=master)](https://travis-ci.org/qateam123/secure-messaging-api)

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

Run the application
-------------------
```
$ python api.py
 * Running on http://127.0.0.1:5000/
 * Restarting with reloader
```

Test the response
-----------------

Now open up a new prompt to test out your API using curl
```
$ curl http://127.0.0.1:5000/
{"hello": "world"}
```