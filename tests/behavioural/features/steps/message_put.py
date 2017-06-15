from flask import json
import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.repository import database
from flask import current_app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings

url = "http://localhost:5050/message/{}/modify"
token_data = {
            "user_uuid": "000000000",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'business_name': 'ABusiness',
        'survey': 'survey.0000'}

modify_data = {'action': '',
               'label': ''}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['Authorization'] = update_encrypted_jwt()


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
def step_impl_message_is_archived(context):
    modify_data['action'] = 'add'
    modify_data['label'] = 'ARCHIVE'
    token_data['user_urn'] = data['urn_from']
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('check message is marked as archived')
def step_impl_assert_message_is_marked_as_archived(context):
    context.response = app.test_client().get("http://localhost:5050/message/{}".format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true('ARCHIVE' in response['labels'])


# Scenario: deleting the "archived" label from a given message
@given("the message is archived")
def step_impl_the_message_is_archived(context):
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


# Scenario: Modifying the status of the message to "unread"
@given('a message has been read')
def step_impl_message_has_been_read(context):
    reset_db()
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    token_data['user_uuid'] = 'respondent.122342'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']

    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    token_data['user_uuid'] = 'internal.12344'
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


# Scenario: modifying the status of the message so that "unread" is removed


@when("the message is marked read")
def step_impl_the_message_is_marked_read(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = "UNREAD"
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


# Scenario: validating a request where there is no label provided
@given('a message is sent')
def step_impl_a_message_is_sent(context):
    reset_db()
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when('the label is empty')
def step_impl_the_label_is_empty(context):
    modify_data['action'] = 'add'
    modify_data['label'] = ''
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('a Bad Request error is returned')
def step_impl_a_bad_request_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


#  Scenario: validating a request where there is no action provided

@when('the action is empty')
def step_impl_the_action_is_empty(context):
    modify_data['action'] = ''
    modify_data['label'] = 'SENT'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('a Bad Request 400 error is returned')
def step_impl_a_bad_request_400_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


# Scenario: validating a request where there in an invalid label provided

@when('an invalid label is provided')
def step_impl_an_invalid_label_is_provided(context):
    modify_data['action'] = ''
    modify_data['label'] = 'DELETED'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('display a Bad Request is returned')
def step_impl_display_a_bad_request_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


#  Scenario: validating a request where there in an invalid action provided
@when('an invalid action is provided')
def step_impl_an_invalid_action_is_provided(context):
    modify_data['action'] = ''
    modify_data['label'] = 'ARCHIVE'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('show a Bad Request is returned')
def step_impl_a_bad_request_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


#  Scenario: validating a request where there in an unmodifiable label is provided
@when('an unmmodifiable label is provided')
def step_impl_an_unmodifiable_label_is_provided(context):
    modify_data['action'] = ''
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=flask.json.dumps(modify_data), headers=headers)


@then('a Bad Request is displayed to the user')
def step_impl_a_bad_request_is_displayed(context):
    nose.tools.assert_equal(context.response.status_code, 400)


# Scenario - internal - message status automatically changes to read - on opening message
@given("a message with the status 'unread' is shown to an internal user")
def step_impl_message_with_status_unread_shown_to_the_user(context):
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the internal user opens the message")
def step_impl_an_internal_user_opens_the_message(context):
    token_data['user_urn'] = data['urn_from']
    headers['Authorization'] = update_encrypted_jwt()
    response_get = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    context.get_json = json.loads(response_get.data)


@then("the status of the message changes from 'unread' to 'read' for all internal users that have access to that survey")
def step_impl_no_unread_messages_returned(context):
    nose.tools.assert_true("UNREAD" not in context.get_json['labels'])


# Scenario - internal - as an internal user I want to be able to change my message from read to unread
@given("a message with the status read is displayed to an internal user")
def step_impl_message_with_status_read_returned(context):
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
    nose.tools.assert_true('UNREAD' in response['labels'])


@given("a message with the status unread is displayed to an internal user")
def step_impl_message_status_unread_returned(context):
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the internal user chooses to edit the status from unread to read")
def step_impledit_status_from_unread_to_read(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    app.test_client().put(url.format(context.msg_id), data=flask.json.dumps(modify_data), headers=headers)


@then("the status of that message changes to read for all internal users that have access to that survey")
def step_impl_message_status_chanegs_to_read(context):
    request = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    request_data = json.loads(request.data)
    nose.tools.assert_true("UNREAD" not in request_data['labels'])


# Scenario: As an external user - message status automatically changes to read - on opening message
@given("a message with the status 'unread' is shown to an external user")
def step_impl_message_status_unread_returned(context):
    response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the external user opens the message")
def step_impl_external_user_opens_the_message(context):
    request = app.test_client().get("http://localhost:5050/message/{0}".format(context.msg_id), headers=headers)
    context.request_data = json.loads(request.data)


@then("the status of the message changes to from unread to read")
def step_impl_message_statis_changes_from_unread_to_read(context):
    nose.tools.assert_true("UNREAD" not in context.request_data['labels'])


# Scenario - external - as an external user I want to be able to change my message from read to unread
@given("a message with the status read is displayed to an external user")
def step_implmessage_with_status_read_returned(context):
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
    nose.tools.assert_true("UNREAD" in request_data['labels'])


@given("a message with the status unread is displayed to an external user")
def step_impl_message_with_Status_unread_returned(context):
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


# If an incorrect message id is requested by the user return a 404 error
@given("a user requests a message with a invalid message id")
def step_impl_return_message_with_invalid_msg_id(context):
    context.msg_id = "RandomMsgIDsdhkbgjksdlfknbsjdshbfjskgbhdhdghgdhdfsdhjghbskggdh"


@when("it is searched for")
def step_impl_searched_for(context):
    modify_data['action'] = 'remove'
    modify_data['label'] = 'UNREAD'
    context.response = app.test_client().put(url.format(context.msg_id),
                                             data=json.dumps(modify_data), headers=headers)


@then("a 404 error code is returned")
def step_impl_404_returned(context):
    nose.tools.assert_equal(context.response.status_code, 404)
