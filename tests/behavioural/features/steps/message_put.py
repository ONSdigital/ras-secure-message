import nose.tools
import flask
from flask import json
from behave import given, then, when
from app.application import app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings, constants

url = "http://localhost:5050/message/{}/modify"
token_data = {
            constants.USER_IDENTIFIER: "ce12b958-2a5f-44f4-a6da-861e59070a31",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
        'msg_from': 'ce12b958-2a5f-44f4-a6da-861e59070a31',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'collection_exercise': 'collection exercise1',
        'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
        'survey': 'BRES'}

modify_data = {'action': '',
               'label': ''}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)


headers['Authorization'] = update_encrypted_jwt()


# Scenario 1: modifying the status of the message to "archived"
@when("the message is archived")
def step_impl_message_is_archived(context):
    modify_data['action'] = 'add'
    modify_data['label'] = 'ARCHIVE'
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is marked as archived')
def step_impl_assert_message_is_marked_as_archived(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('ARCHIVE' in response['labels'])


# Scenario 2: deleting the "archived" label from a given message
@given("the message is archived")
def step_impl_the_message_is_archived(context):
    data['msg_to'] = ['BRES']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']

    modify_data['action'] = 'add'
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@when("the message is unarchived")
def step_impl_message_is_unarchived(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = "ARCHIVE"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is not marked as archived')
def step_impl_message_not_marked_archived(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('ARCHIVE' not in response)


# Scenario 3: Modifying the status of the message to "unread"
@given('a message has been read')
def step_impl_message_has_been_read(context):
    data['msg_to'] = ['BRES']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']

    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    modify_data['msg_from'] = 'BRES'
    token_data[constants.USER_IDENTIFIER] = 'BRES'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@when("the message is marked unread")
def step_impl_message_marked_unread(context):
    modify_data['action'] = 'add'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is marked unread')
def step_imp_check_message_is_marked_unread(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('UNREAD' in response['labels'])


# Scenario 4: modifying the status of the message so that "unread" is removed
@when("the message is marked read")
def step_impl_the_message_is_marked_read(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = "UNREAD"
    token_data[constants.USER_IDENTIFIER] = 'BRES'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is not marked unread')
def step_impl_check_message_is_not_marked_unread(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('UNREAD' not in response['labels'])


@then('message read date should be set')
def step_impl_message_read_date_should_be_set(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['read_date'])


# Scenario 5: validating a request where there is no label provided
@when('the label is empty')
def step_impl_the_label_is_empty(context):
    modify_data['action'] = 'add'
    modify_data['label'] = ''
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


# Scenario 6: validating a request where there is no action provided
@when('the action is empty')
def step_impl_the_action_is_empty(context):
    modify_data['action'] = ''
    modify_data['label'] = 'SENT'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


# Scenario 7: validating a request where there in an invalid label provided
@when('an invalid label is provided')
def step_impl_an_invalid_label_is_provided(context):
    modify_data['action'] = ''
    modify_data['label'] = 'DELETED'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


# Scenario 8: validating a request where an invalid action provided
@when('an invalid action is provided')
def step_impl_an_invalid_action_is_provided(context):
    modify_data['action'] = ''
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


# Scenario 9: validating a request where there in an unmodifiable label is provided
@when('an unmodifiable label is provided')
def step_impl_an_unmodifiable_label_is_provided(context):
    modify_data['action'] = ''
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


# Scenario 10: internal - message status automatically changes to read - on opening message
@given("a message with the status 'unread' is shown to an internal user")
def step_impl_message_with_status_unread_shown_to_the_user(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the internal user opens the message")
def step_impl_an_internal_user_opens_the_message(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    headers['Authorization'] = update_encrypted_jwt()
    response_get = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    context.get_json = json.loads(response_get.data)


@then("the status of the message changes from 'unread' to 'read' for all internal users that have access to that survey")
def step_impl_no_unread_messages_returned(context):
    nose.tools.assert_true("UNREAD" not in context.get_json['labels'])


# Scenario 11: internal - as an internal user I want to be able to change my message from read to unread
@given("a message with the status read is displayed to an internal user")
def step_impl_message_with_status_read_returned(context):
    data['msg_to'] = ['BRES']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']

    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@when("the internal user chooses to edit the status from read to unread")
def step_impl_edit_status_read_to_unread(context):
    modify_data['action'] = 'add'
    modify_data['label'] = "UNREAD"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then("the status of that message changes to unread for all internal users that have access to that survey")
def step_impl_status_of_message_changes_to_unread(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('READ' not in response['labels'])


# Scenario 12: internal - as an internal user I want to be able to change my message from unread to read
@given("a message with the status unread is displayed to an internal user")
def step_impl_message_status_unread_returned(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the internal user chooses to edit the status from unread to read")
def step_impl_edit_status_from_unread_to_read(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    app.test_client().put(url.format(context.msg_id), data=flask.json.dumps(modify_data), headers=headers)


@then("the status of that message changes to read for all internal users that have access to that survey")
def step_impl_message_status_chanegs_to_read(context):
    request = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    request_data = json.loads(request.data)
    nose.tools.assert_true("UNREAD" not in request_data['labels'])


# Scenario 13: external - message status automatically changes to read - on opening message
@given("a message with the status 'unread' is shown to an external user")
def step_impl_message_status_unread_returned(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the external user opens the message")
def step_impl_external_user_opens_the_message(context):
    request = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    context.request_data = json.loads(request.data)


@then("the status of the message changes to from unread to read")
def step_impl_message_status_changes_from_unread_to_read(context):
    nose.tools.assert_true("UNREAD" not in context.request_data['labels'])


# Scenario 14: external - as an external user I want to be able to change my message from read to unread
@given("a message with the status read is displayed to an external user")
def step_implmessage_with_status_read_returned(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']
    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    app.test_client().put(url.format(context.msg_id), data=flask.json.dumps(modify_data), headers=headers)


@when("the external user chooses to edit the status from read to unread")
def step_impl_external_user_edits_status_from_read_to_unread(context):
    modify_data['action'] = 'add'
    modify_data['label'] = 'UNREAD'
    app.test_client().put(url.format(context.msg_id), data=flask.json.dumps(modify_data), headers=headers)


@then("the status of that message changes to unread")
def step_impl_the_status_of_the_message_changes_to_unread(context):
    request = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    request_data = json.loads(request.data)
    nose.tools.assert_true("READ" not in request_data['labels'])


# Scenario 15: external - as an external user I want to be able to change my message from unread to read
@given("a message with the status unread is displayed to an external user")
def step_impl_message_with_status_unread_returned(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the external user chooses to edit the status from unread to read")
def step_impl_edit_status_from_unread_to_read(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    app.test_client().put(url.format(context.msg_id), data=flask.json.dumps(modify_data), headers=headers)


@then("the status of that message changes to read")
def step_impl_assert_message_status_changes_to_read(context):
    request = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    request_data = json.loads(request.data)
    nose.tools.assert_true("UNREAD" not in request_data['labels'])


# Scenario 16: If an incorrect message id is requested by the user return a 404 error
@given("a user requests a message with a invalid message id")
def step_impl_return_message_with_invalid_msg_id(context):
    context.msg_id = "RandomMsgIDsdhkbgjksdlfknbsjdshbfjskgbhdhdghgdhdfsdhjghbskggdh"


@when("it is searched for")
def step_impl_searched_for(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=json.dumps(modify_data), headers=headers)

# Scenario 17: As a user I should receive an error if I attempt to mark a message as read that is not in my inbox
@given("a user has sent a message")
def step_impl_a_message_is_sent(context):
    data['msg_to'] = ['BRES']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['user_uuid'] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']

@when("I attempt to mark a message as read")
def step_impl_a_message_is_marked_as_read(context):
    modify_data['action'] = 'add'
    modify_data['label'] = "READ"
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)

# Common Steps: used in multiple scenarios
@given("a valid message is sent")
def step_impl(context):
    data['msg_to'] = ['BRES']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@given('a message is sent')
def step_impl_a_message_is_sent(context):
    data['msg_to'] = ['BRES']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']
