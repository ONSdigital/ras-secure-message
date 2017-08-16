import nose.tools
from flask import json
from behave import given, then, when
from app.application import app
from app.repository import database
from app.common.alerts import AlertUser, AlertViaGovNotify
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings, constants
from flask import current_app
from unittest import mock


url = "http://localhost:5050/message/send"
token_data = {
            constants.USER_IDENTIFIER: "000000000",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}
data = {}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)


headers['Authorization'] = update_encrypted_jwt()


def before_scenario(context):
    AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()

    data.update({
                 'msg_to': [constants.BRES_USER],
                 'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'collection_exercise': 'collection exercise1',
                 'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                 'survey': constants.BRES_SURVEY})


# Scenario 1: Submitting a valid message and receiving a 201
@given('a valid message')
def step_impl_a_valid_message(context):
    before_scenario(context)


# Scenario 2: Send a draft and receive a 201
# Scenario 3: Send a draft and receive a msg_id (see common code)
# Scenario 4: A user sends a previously saved draft
@given('a user retrieves a previously saved draft')
def step_impl_user_retrieves_draft(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)
    context.message = json.loads(get_draft.data)


# Scenario 5: Send a draft and receive a thread_id
@then('thread_id is the same as msg_id')
def step_impl_thread_id_and_msg_id_are_equal(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_equal(resp['thread_id'], resp['msg_id'])


# Scenario 6: Send a draft and receive a msg_id (see common code)
# Scenario 7: Send a draft which is a reply to another message

@given('a message is identified as a draft which is a reply to another message')
def step_impl_a_message_is_a_draft_reply(context):
    data.update({'msg_to': [constants.BRES_USER],
                 'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '25e9172c-62d9-4ff7-98ac-661300ae9446',
                 'collection_case': 'collection case1',
                 'collection_exercise': 'collection exercise1',
                 'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                 'survey': constants.BRES_SURVEY})

    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'msg_to': [constants.BRES_USER],
                       'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': '25e9172c-62d9-4ff7-98ac-661300ae9446',
                       'collection_case': 'collection case1',
                       'collection_exercise': 'collection exercise1',
                       'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                       'survey': constants.BRES_SURVEY}


@then('thread_id is not the same as msg_id')
def step_impl_thread_id_and_msg_id_are_not_equal(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_not_equals(resp['thread_id'], resp['msg_id'])
    nose.tools.assert_equal(resp['thread_id'], '25e9172c-62d9-4ff7-98ac-661300ae9446')


# Scenario 8: Submit a message with a missing "To" field and receive a 400 error
@given("the 'To' field is empty")
def step_impl_to_field_empty(context):
    data['msg_to'] = ['']


# Scenario 9: Submit a message with a missing "From" field and receive a 400 error
@given("the 'From' field is empty")
def step_impl_from_field_empty(context):
    data['msg_from'] = ''


# Scenario 10: Submit a message with a missing "Body" field and receive a 400 error
@given("the 'Body' field is empty")
def step_impl_body_field_empty(context):
    data['body'] = ''


# Scenario 11: Submit a message with a missing "Subject" field and receive a 400
@given("the 'Subject' field is empty")
def step_impl_subject_field_empty(context):
    data['subject'] = ""


# Scenario 12: Message sent without a thread id
@given("the 'Thread ID' field is empty")
def step_impl_thread_id_field_empty(context):
    before_scenario(context)
    data['thread_id'] = ''


# Scenario 13: Message sent with a msg_to too long
@given("the 'To' field exceeds max limit in size")
def step_impl_to_field_exceeds_max_limit(context):
    data['msg_to'] = ["x" * (constants.MAX_TO_LEN+1)]


# Scenario 14: Message sent with a msg_from too long
@given("the 'From' field exceeds max limit in size")
def step_impl_from_field_exceeds_max_limit(context):
    data['msg_from'] = "y" * (constants.MAX_FROM_LEN+1)


# Scenario 15: Message sent with an empty survey field return 400
@given('the survey field is empty')
def step_impl_survey_field_empty(context):
    data['survey'] = ''


# Scenario 16: Send a message with a msg_id not a valid draft returns 400
@given('a message contains a msg_id and is not a valid draft')
def step_impl_message_contains_msg_id_and_is_not_valid_draft(context):
    data.update({'msg_id': 'test123',
                 'msg_to': [constants.BRES_USER],
                 'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'collection_exercise': 'collection exercise1',
                 'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                 'survey': constants.BRES_SURVEY})


# Scenario 17: When a message with the label of "Draft" is sent and another user is trying to send the same message return a 409
@given('a draft message is posted')
def step_impl_draft_message_posted(context):
    if 'msg_id' in data:
        del data['msg_id']

    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    # get etag from response using context
    context.etag = json.loads(context.post_draft.data)
    headers['Etag'] = context.etag

    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'msg_to': [constants.BRES_USER],
                       'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': '',
                       'collection_case': 'collection case1',
                       'collection_exercise': 'collection exercise1',
                       'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                       'survey': constants.BRES_SURVEY}

    token_data[constants.USER_IDENTIFIER] = context.message['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post(url, data=json.dumps(context.message), headers=headers)


@when('another user tries to send the same message')
def step_impl_another_user_sends_same_message(context):
    data.update({'msg_id': context.msg_id,
                 'msg_to': [constants.BRES_USER],
                 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                 'subject': 'test',
                 'body': 'test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'collection_exercise': 'collection exercise1',
                 'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                 'survey': constants.BRES_SURVEY})

    data['subject'] = 'edited'
    headers['Etag'] = context.etag

    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post(url.format(context.msg_id),
                                              data=json.dumps(data), headers=headers)


# Scenario 18: A Etag is not present within the header
@given('a message is created')
def step_impl_message_is_created(context):
    context.msg = {'msg_to': [constants.BRES_USER],
                   'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                   'subject': 'test',
                   'body': 'Test',
                   'thread_id': '',
                   'collection_case': 'collection case1',
                   'collection_exercise': 'collection exercise1',
                   'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                   'survey': constants.BRES_SURVEY}


@when('the message is sent with no Etag')
def step_impl_message_sent_no_etag(context):
    if 'ETag' in headers:
        del headers['ETag']

    token_data[constants.USER_IDENTIFIER] = context.msg['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    context.response = app.test_client().post(url, data=json.dumps(context.msg), headers=headers)


# Scenario 19: Send a message where msg_to is a string
@given('a msg_to is entered as a string')
def step_impl_msg_to_string(context):
    context.message = {'msg_to': [constants.BRES_USER],
                       'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': '',
                       'collection_case': 'collection case1',
                       'collection_exercise': 'collection exercise1',
                       'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                       'survey': constants.BRES_SURVEY}
    isinstance(data['msg_to'], str)


# Common Steps: used in multiple scenarios
@given('a message is identified as a draft')
def step_impl_a_message_is_a_draft(context):
    token_data[constants.USER_IDENTIFIER] = '01b51fcc-ed43-4cdb-ad1c-450f9986859b'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'msg_to': [constants.BRES_USER],
                       'msg_from': '01b51fcc-ed43-4cdb-ad1c-450f9986859b',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': context.msg_id,
                       'collection_case': 'collection case1',
                       'collection_exercise': 'collection exercise1',
                       'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                       'survey': constants.BRES_SURVEY}


@when("the message is sent with msg_to string")
def step_impl_message_is_sent(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post(url, data=json.dumps(context.message), headers=headers)


@when('the draft is sent')
def step_impl_draft_is_sent(context):
    context.response = app.test_client().post(url, data=json.dumps(context.message), headers=headers)


@when("the message is sent")
def step_impl_msg_is_sent(context):
    token_data[constants.USER_IDENTIFIER] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post(url, data=json.dumps(data), headers=headers)


@then('a msg_id in the response')
def step_impl_msg_id_in_response(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_true(resp['msg_id'] is not None)


@then('a thread_id in the response')
def step_impl_thread_id_in_response(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_true(resp['thread_id'] is not None)


@given('a message to an unknown user is created')
def step_impl_a_message_to_unknown_user(context):
    context.msg = {'msg_to': ['UnknownUser'],
                   'msg_from': constants.BRES_USER,
                   'subject': 'test',
                   'body': 'Test',
                   'thread_id': '',
                   'collection_case': 'collection case1',
                   'collection_exercise': 'collection exercise1',
                   'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                   'survey': constants.BRES_SURVEY}


@when('the created message is sent')
def step_impl_created_message_is_sent(context):
    token_data[constants.USER_IDENTIFIER] = context.msg['msg_from']
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post("http://localhost:5050/message/send", data=json.dumps(context.msg),
                                              headers=headers)
