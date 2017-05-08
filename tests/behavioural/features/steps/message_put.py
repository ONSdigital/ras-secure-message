import uuid
from flask import json
import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.repository import database
from flask import current_app

url = "http://localhost:5050/message/{}/modify"
headers = {'Content-Type': 'application/json', 'user_urn': 'internal.12344'}

data = {'urn_to': 'test',
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


# Scenario: modifying the status of the message to "archived"
@given("a valid message is sent")
def step_impl(context):
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when("the message is archived")
def step_impl(context):
    modify_data['action'] = 'add'
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is marked as archived')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('ARCHIVE' in response['labels'])


# Scenario: deleting the "archived" label from a given message
@given("the message is archived")
def step_impl(context):
    reset_db()
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']

    modify_data['action'] = 'add'
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@when("the message is unarchived")
def step_impl(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = "ARCHIVE"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is not marked as archived')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('ARCHIVE' not in response)


# Scenario: Modifying the status of the message to "unread"
@given('a message has been read')
def step_impl(context):
    reset_db()
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']

    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@when("the message is marked unread")
def step_impl(context):
    modify_data['action'] = 'add'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is marked unread')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('UNREAD' in response['labels'])


# Scenario: modifying the status of the message so that "unread" is removed


@when("the message is marked read")
def step_impl(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is not marked unread')
def step_impl(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('UNREAD' not in response['labels'])


@then('message read date should be set')
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['read_date'])


# Scenario: validating a request where there is no label provided
@given('a message is sent')
def step_impl(context):
    reset_db()
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when('the label is empty')
def step_impl(context):
    modify_data['action'] = 'add'
    modify_data['label'] = ''
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('a Bad Request error is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


#  Scenario: validating a request where there is no action provided

@when('the action is empty')
def step_impl(context):
    modify_data['action'] = ''
    modify_data['label'] = 'SENT'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('a Bad Request 400 error is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


# Scenario: validating a request where there in an invalid label provided

@when('an invalid label is provided')
def step_impl(context):
    modify_data['action'] = ''
    modify_data['label'] = 'DELETED'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('display a Bad Request is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


#  Scenario: validating a request where there in an invalid action provided
@when('an invalid action is provided')
def step_impl(context):
    modify_data['action'] = ''
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('show a Bad Request is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


#  Scenario: validating a request where there in an unmodifiable label is provided
@when('an unmmodifiable label is provided')
def step_impl(context):
    modify_data['action'] = ''
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('a Bad Request is displayed to the user')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)

# Scenario: internal - message status automatically changes to read - on opening message


@given("a message with the status 'unread' is displayed to an internal user")
def step_impl(context):
    data['urn_to'] = 'internal.123'
    context.response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)


@when("the internal user opens the message")
def step_impl(context):
    response = json.loads(context.response.data)
    msg_id = response['msg_id']
    headers['user_urn'] = data['urn_from']
    response_get = app.test_client().get("http://localhost:5050/message/{0}".format(msg_id), headers=headers)
    context.get_json = json.loads(response_get.data)


@then("the status of the message changes to from 'unread' to 'read' for all internal users")
def step_impl(context):
    nose.tools.assert_true('UNREAD' not in context.get_json['labels'])

# Scenario: internal - as an internal user I want to be able to change my message from read to unread


@given("a message with the status read is displayed to an internal user")
def step_impl(context):
    data['urn_to'] = 'internal.123'
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    post_resp = json.loads(response.data)
    context.msg_id = post_resp['msg_id']
    modify_data['action'] = 'remove'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    headers['user_urn'] = data['urn_from']
    app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)


@when("the user chooses to edit the status from read to unread")
def step_impl(context):
    modify_data['action'] = 'add'
    modify_data['label'] = "UNREAD"
    app.test_client().put(url.format(context.msg_id),
                          data=flask.json.dumps(modify_data), headers=headers)


@then("the status of that message changes to unread for all internal users that have access to that work group")
def step_impl(context):
    response_get = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    data_get = json.loads(response_get.data)
    nose.tools.assert_true("UNREAD" in data_get['labels'])


# Scenario: As an external user - message status automatically changes to read - on opening message
@given("a message with the status 'unread' is displayed to an external user")
def step_impl(context):
    data['urn_to'] = 'respondent.123'
    context.response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)


@when("the external user opens the message")
def step_impl(context):
    response = json.loads(context.response.data)
    msg_id = response['msg_id']
    headers['user_urn'] = data['urn_from']
    response_get = app.test_client().get("http://localhost:5050/message/{0}".format(msg_id), headers=headers)
    context.get_json = json.loads(response_get.data)


@then("the status of the message changes to from 'unread' to 'read'")
def step_impl(context):
    nose.tools.assert_true('UNREAD' not in context.get_json['labels'])


# Scenario: As an external user I want to be able to change the status of my message from read to unread
@given("a message with the status 'read' is displayed to an external user")
def step_impl(context):
    data['urn_to'] = 'respondent.123'
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    post_resp = json.loads(response.data)
    context.msg_id = post_resp['msg_id']
    modify_data['action'] = 'remove'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    headers['user_urn'] = data['urn_from']
    app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)


@when("the external user chooses to edit the status from 'read' to 'unread'")
def step_impl(context):
    modify_data['action'] = 'add'
    modify_data['label'] = "UNREAD"
    app.test_client().put(url.format(context.msg_id),
                          data=flask.json.dumps(modify_data), headers=headers)


@then("the status of that message changes to 'unread'")
def step_impl(context):
    response_get = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    data_get = json.loads(response_get.data)
    nose.tools.assert_true("UNREAD" in data_get['labels'])

# Scenario: As an internal user I want to be able to edit a message from my drafts


@given("a message with the status read is displayed to an external user")
def step_impl(context):
    context.response = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data), headers=headers)
