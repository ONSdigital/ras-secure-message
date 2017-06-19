import flask
from flask import json
import nose.tools
from behave import given, then, when
from app.application import app
import uuid
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings

url = "http://localhost:5050/message/{0}"
token_data = {
            "user_uuid": "000000000",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'msg_to': 'test',
        'msg_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'business_name': 'ABusiness',
        'survey': 'BRES'}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['Authorization'] = update_encrypted_jwt()


# Scenario: Retrieve a message with correct message ID
@given("there is a message to be retrieved")
def step_impl_there_is_a_message_to_be_retrieved(context):
    data['msg_to'] = 'BRES'
    data['msg_from'] = 'respondent.122342'
    token_data['user_uuid'] = 'respondent.122342'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                              headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when("the get request is made with a correct message id")
def step_impl_the_get_request_is_made_with_a_correct_message_id(context):
    token_data['user_uuid'] = 'respondent.122342'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.msg_id), headers=headers)


@then("a 200 HTTP response is returned")
def step_impl_a_200_http_response_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 200)


@then("returned message field msg_to is correct")
def step_impl_correct_msg_to_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_to'], [data['msg_to']])


@then("returned message field msg_from is correct")
def step_impl_correct_msg_from_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_from'], data['msg_from'])


@then("returned message field body is correct")
def step_impl_correct_body_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['body'], data['body'])


@then("returned message field subject is correct")
def step_impl_correct_subject_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['subject'], data['subject'])


@then("returned message field ReportingUnit is correct")
def step_impl_correct_reporting_unit_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['reporting_unit'], data['reporting_unit'])


@then("returned message field CollectionCase is correct")
def step_impl_correct_collection_case_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_case'], data['collection_case'])


@then("returned message field BusinessName is correct")
def step_impl_correct_business_name_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['business_name'], data['business_name'])


# Scenario: Retrieve a message with incorrect message ID
@when("the get request has been made with an incorrect message id")
def step_impl_the_get_request_has_been_made_with_incorrect_message_id(context):
    context.response = app.test_client().get(url.format(str(uuid.uuid4())), headers=headers)


@then("a 404 HTTP response is returned")
def step_impl_a_404_http_response_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 404)


# Scenario: Respondent sends message and retrieves the same message with it's labels
@given("a respondent sends a message")
def step_impl_a_respondent_sends_a_message(context):
    data['msg_to'] = 'internal.12344'
    data['msg_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when("the respondent wants to see the message")
def step_impl_the_respondent_wants_to_see_the_message(context):
    token_data['user_uuid'] = 'respondent.122342'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.msg_id), headers=headers)


@then("the retrieved message should have the label SENT")
def step_impl_the_retrieved_message_should_have_label_sent(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['labels'], ['SENT'])


# Scenario: Internal user sends message and retrieves the same message with it's labels
@given("an internal user sends a message")
def step_impl_an_internal_user_sends_a_message(context):
    data['msg_to'] = 'respondent.122342'
    data['msg_from'] = 'BRES'
    token_data['user_uuid'] = 'internal.12344'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when("the internal user wants to see the message")
def step_impl_the_internal_user_wants_to_see_the_message(context):
    token_data['user_uuid'] = 'internal.12344'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.msg_id), headers=headers)


#  Scenario: Internal user sends message and respondent retrieves the same message with it's labels
@then("the retrieved message should have the labels INBOX and UNREAD")
def step_impl_the_retrieved_message_should_havethe_labels_inbox_and_unread(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true(len(response['labels']), 2)
    nose.tools.assert_true('INBOX' in response['labels'])
    nose.tools.assert_true('UNREAD' in response['labels'])


#   Scenario: Retrieve a draft message

@given('there is a draft message to be retrieved')
def step_impl_draft_message_can_be_retrieved(context):
    token_data['user_uuid'] = '9976a558-c529-4652-806e-fac1b8d4fdcb'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    data.update({'msg_from': '9976a558-c529-4652-806e-fac1b8d4fdcb',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'BRES'})
    response = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                      headers=headers)
    context.resp_data = json.loads(response.data)


@when('the get request is made with a draft message id')
def step_impl_the_draft_is_requested(context):
    token_data['user_uuid'] = '9976a558-c529-4652-806e-fac1b8d4fdcb'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.resp_data['msg_id']), headers=headers)


@then('message returned is a draft')
def step_impl_assert_returned_is_draft(context):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(response['msg_id'], context.resp_data['msg_id'])
    nose.tools.assert_in("DRAFT", response['labels'])



