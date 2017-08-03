import uuid

import flask
import nose.tools
from behave import given, then, when
from flask import json
from app.api_mocks import party_service_mock
from app import settings, constants
from app.application import app
from app.authentication.jwe import Encrypter
from app.authentication.jwt import encode

url = "http://localhost:5050/message/{0}"
token_data = {
            constants.USER_IDENTIFIER: "000000000",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'msg_to': ['test'],
        'msg_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'collection_exercise': 'collection exercise1',
        'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
        'survey': 'BRES'}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)


headers['Authorization'] = update_encrypted_jwt()


# Scenario 1: Retrieve a correct message with message ID
@when("the get request is made with a correct message id")
def step_impl_the_get_request_is_made_with_a_correct_message_id(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.msg_id), headers=headers)


# Scenario 2: Retrieve a draft message
@when('the get request is made with a draft message id')
def step_impl_the_draft_is_requested(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.resp_data['msg_id']), headers=headers)


@then('message returned is a draft')
def step_impl_assert_returned_is_draft(context):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(response['msg_id'], context.resp_data['msg_id'])
    nose.tools.assert_in("DRAFT", response['labels'])


# Scenario 3: Retrieve the correct draft message (see common code)
# Scenario 4: Retrieve a message with incorrect message ID
@when("the get request has been made with an incorrect message id")
def step_impl_the_get_request_has_been_made_with_incorrect_message_id(context):
    context.response = app.test_client().get(url.format(str(uuid.uuid4())), headers=headers)


# Scenario 5: Respondent sends message and retrieves the same message with it's labels
@when("the respondent wants to see the message")
def step_impl_the_respondent_wants_to_see_the_message(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.msg_id), headers=headers)


# Scenario 6: Internal user sends message and retrieves the same message with it's labels
@when("the internal user wants to see the message")
def step_impl_the_internal_user_wants_to_see_the_message(context):
    token_data[constants.USER_IDENTIFIER] = 'ce12b958-2a5f-44f4-a6da-861e59070a31'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(context.msg_id), headers=headers)


# Scenario 7: Internal user sends message and respondent retrieves the same message with it's labels
@then("the retrieved message should have the labels INBOX and UNREAD")
def step_impl_the_retrieved_message_should_havethe_labels_inbox_and_unread(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true(len(response['labels']), 2)
    nose.tools.assert_true('INBOX' in response['labels'])
    nose.tools.assert_true('UNREAD' in response['labels'])


# Common Steps: used in multiple scenarios
@given("there is a message to be retrieved")
def step_impl_there_is_a_message_to_be_retrieved(context):
    data['msg_to'] = ['BRES']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                              headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@given('there is a draft message to be retrieved')
def step_impl_draft_message_can_be_retrieved(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    data.update({'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'collection_exercise': 'collection exercise1',
                 'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                 'survey': 'BRES'})
    response = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                      headers=headers)
    context.resp_data = json.loads(response.data)


@given("an internal user sends a message")
def step_impl_an_internal_user_sends_a_message(context):
    data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
    data['msg_from'] = 'BRES'
    token_data[constants.USER_IDENTIFIER] = 'ce12b958-2a5f-44f4-a6da-861e59070a31'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@given("a respondent sends a message")
def step_impl_a_respondent_sends_a_message(context):
    data['msg_to'] = ['ce12b958-2a5f-44f4-a6da-861e59070a31']
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                              data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@then("returned message field msg_to is correct")
def step_impl_correct_msg_to_returned(context):
    msg_resp = json.loads(context.response.data)
    msg_to = party_service_mock._respondent_ids[data['msg_to'][0]]
    nose.tools.assert_equal(msg_resp['msg_to'], [data['msg_to'][0]])
    nose.tools.assert_equal(msg_resp['@msg_to'], [msg_to])


@then("returned message field msg_from is correct")
def step_impl_correct_msg_from_returned(context):
    msg_resp = json.loads(context.response.data)
    msg_from = party_service_mock._respondent_ids[data['msg_from']]
    nose.tools.assert_equal(msg_resp['@msg_from'], msg_from)
    nose.tools.assert_equal(msg_resp['msg_from'], data['msg_from'])


@then("returned message field body is correct")
def step_impl_correct_body_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['body'], data['body'])


@then("returned message field subject is correct")
def step_impl_correct_subject_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['subject'], data['subject'])


@then("returned message field RU_id is correct")
def step_impl_correct_ru_id_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['ru_id'], 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc')


@then("returned message field CollectionCase is correct")
def step_impl_correct_collection_case_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_case'], data['collection_case'])


@then("returned message field CollectionExercise is correct")
def step_impl_correct_collection_exercise_returned(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_exercise'], data['collection_exercise'])


@then("the retrieved message should have the label SENT")
def step_impl_the_retrieved_message_should_have_label_sent(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['labels'], ['SENT'])
