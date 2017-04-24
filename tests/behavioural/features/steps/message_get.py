import flask
import nose.tools
from behave import given, then, when
from app.application import app
import uuid

url = "http://localhost:5050/message/"
headers = {'Content-Type': 'application/json', 'user_urn': ''}

data = {'msg_id': '',
        'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'survey': 'survey'}


# Scenario: Retrieve a message with correct message ID
@given("there is a message to be retrieved")
def step_impl(context):
    data['msg_id'] = str(uuid.uuid4())
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)


@when("the get request is made with a correct message id")
def step_impl(context):
    new_url = url+data['msg_id']
    context.response = app.test_client().get(new_url, headers=headers)


@then("a 200 HTTP response is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 200)


# Scenario: Retrieve a message with incorrect message ID
@when("the get request has been made with an incorrect message id")
def step_impl(context):
    new_url = url+str(uuid.uuid4())
    context.response = app.test_client().get(new_url, headers=headers)


@then("a 404 HTTP response is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 404)


# Scenario: Respondent sends message and retrieves the same message with it's labels
@given("a respondent sends a message")
def step_impl(context):
    data['msg_id'] = str(uuid.uuid4())
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)


@when("the respondent wants to see the message")
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    new_url = url+data['msg_id']
    context.response = app.test_client().get(new_url, headers=headers)


@then("the retrieved message should have the label SENT")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['labels'], ['SENT'])


# Scenario: Internal user sends message and retrieves the same message with it's labels
@given("an internal user sends a message")
def step_impl(context):
    data['msg_id'] = str(uuid.uuid4())
    data['urn_to'] = 'respondent.122342'
    data['urn_from'] = 'internal.12344'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)


@when("the internal user wants to see the message")
def step_impl(context):
    headers['user_urn'] = 'internal.12344'
    new_url = url+data['msg_id']
    context.response = app.test_client().get(new_url, headers=headers)


#  Scenario: Internal user sends message and respondent retrieves the same message with it's labels
@then("the retrieved message should have the labels INBOX and UNREAD")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true(len(response['labels']), 2)
    nose.tools.assert_true('INBOX' in response['labels'])
    nose.tools.assert_true('UNREAD' in response['labels'])
