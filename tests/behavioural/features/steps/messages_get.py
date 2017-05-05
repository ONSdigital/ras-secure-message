import flask
import nose.tools
from behave import given, then, when
from app.application import app
import uuid
from app.repository import database
from flask import current_app

url = "http://localhost:5050/messages"
headers = {'Content-Type': 'application/json', 'user_urn': ''}

data = {'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'survey': 'survey'}


def reset_db():
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()

# Scenario: Respondent sends multiple messages and retrieves the list of messages with their labels


@given("a respondent sends multiple messages")
def step_impl(context):
    reset_db()
    for x in range(0, 2):
        data['urn_to'] = 'internal.12344'
        data['urn_from'] = 'respondent.122342'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                              data=flask.json.dumps(data), headers=headers)


@when("the respondent gets their messages")
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get(url, headers=headers)


@then("the retrieved messages should have the correct SENT labels")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        num = x+1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['SENT'])


# Scenario: Internal user sends multiple messages and retrieves the list of messages with their labels

@given("a Internal user sends multiple messages")
def step_impl(context):
    reset_db()
    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                              data=flask.json.dumps(data), headers=headers)


@when("the Internal user gets their messages")
def step_impl(context):
    headers['user_urn'] = 'internal.122342'
    context.response = app.test_client().get(url, headers=headers)

# Scenario: Respondent sends multiple messages and internal user retrieves the list of messages with their labels
# Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with their labels


@then("the retrieved messages should have the correct INBOX and UNREAD labels")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        num = x+1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['INBOX', 'UNREAD'])
        nose.tools.assert_true(len(response['messages'][str(num)]['labels']), 2)
        nose.tools.assert_true('INBOX' in response['messages'][str(num)]['labels'])
        nose.tools.assert_true('UNREAD' in response['messages'][str(num)]['labels'])

# Scenario: As an external user I would like to be able to view a lst of messages


@given("multiple messages have been sent to an external user")
def step_impl(context):
    for x in range(0, 2):
        data['urn_to'] = 'respondent.123'
        app.test_client().post("http://localhost:5050/message/send", headers=headers)


@when("the external user navigates to their messages")
def step_impl(context):
    headers['user_urn'] = 'respondent.123'
    context.response = app.test_client().get(url, headers=headers)


@then("messages are displayed")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true(len(response['messages']), 2)
