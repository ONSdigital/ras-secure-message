import flask
import nose.tools
from behave import given, then, when
from app import application

url = "http://localhost:5050/message/"
headers = {'Content-Type': 'application/json', 'user_urn': ''}
data = {'msg_id': '9',
         'urn_to': 'test',
         'urn_from': 'test',
         'subject': 'Hello World',
         'body': 'Test',
         'thread_id': '',
         'collection_case': 'collection case1',
         'reporting_unit': 'reporting case1',
         'survey': 'survey'}


# Scenario: Retrieve a message with correct missing ID

@given("there is a message to be retrieved")
def step_impl(context):
    context.response = application.app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)


@when("the get request is made with a correct message id")
def step_impl(context):
    new_url = url+str(9)
    context.response = application.app.test_client().get(new_url, headers=headers)


@then("a 200 HTTP response is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 200)


# Scenario: Retrieve a message with incorrect missing ID


@when("the get request has been made with an incorrect")
def step_impl(context):
    new_url = url+str(2)
    context.response = application.app.test_client().get(new_url, headers=headers)


@then("a 404 HTTP response is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 404)
