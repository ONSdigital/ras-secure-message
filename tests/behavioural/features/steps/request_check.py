import flask
import nose.tools
from behave import given, then, when
from app import application

headers = {'Content-Type': 'application/json', 'user_urn': ''}

# Scenario: Retrieve a message with correct missing ID


@given("no user urn is in the header")
def step_impl(context):
    if 'user_urn' in headers:
        del headers['user_urn']


@when("a GET request is made")
def step_impl(context):
    url = "http://localhost:5050/message/1"
    context.response = application.app.test_client().get(url, headers=headers)


# Scenario: Retrieve a message with incorrect missing ID


@when("a POST request is made")
def step_impl(context):
    url = "http://localhost:5050/message/send"
    context.response = application.app.test_client().post(url, headers=headers)
