import uuid

import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.repository import database
from flask import current_app
from app.repository.database import db

url = "http://localhost:5050/message/{}/modify"
headers = {'Content-Type': 'application/json', 'user_urn': 'internal.12344'}

data = {'msg_id': '',
        'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'survey': 'survey.0000'}

modify_data = {'action': '',
               'label': ''}


def reset_db():
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()


# Scenario: add the "archived" label to the message
@given("a valid message is sent")
def step_impl(context):
    data['msg_id'] = str(uuid.uuid4())
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)


@when("an archived label is added")
def step_impl(context):
    modify_data['action'] = 'add'
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message has label "archived"')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('ARCHIVE' in response['labels'])


# Scenario: deleting the "archived" label from a given message
@given("an archived label is added")
def step_impl(context):
    reset_db()
    data['msg_id'] = str(uuid.uuid4())
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)

    modify_data['action'] = 'add'
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)


@when("the archived label is removed")
def step_impl(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = "ARCHIVE"
    context.response = app.test_client().put(url.format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message does not have label "archived"')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('ARCHIVE' not in response['labels'])


# Scenario: add the "unread" label to the message
@given('a message has been read')
def step_impl(context):
    reset_db()
    data['msg_id'] = str(uuid.uuid4())
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)

    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)


@when("the unread label is added")
def step_impl(context):
    modify_data['action'] = 'add'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message has label "unread"')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('UNREAD' in response['labels'])

    # Scenario: deleting the "unread" level from a given message


@when("the unread label is removed")
def step_impl(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message does not have label "unread"')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(data['msg_id']),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('UNREAD' not in response['labels'])
