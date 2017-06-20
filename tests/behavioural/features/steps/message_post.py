from flask import json
import nose.tools
from behave import given, then, when
from app import constants
from app.application import app
from app.repository import database
from flask import current_app
from unittest import mock
from app.common.alerts import AlertUser, AlertViaGovNotify
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings


url = "http://localhost:5050/message/send"
token_data = {
            "user_uuid": "000000000",
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
                 'msg_to': 'test',
                 'msg_from': 'respondent.test',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})


# Scenario 1: Submitting a valid message and receiving a 201
@given('a valid message')
def step_impl_a_valid_message(context):
    before_scenario(context)


# Scenario 2: Send a draft and receive a 201
@given('a message is identified as a draft')
def step_impl_a_message_is_a_draft(context):
    token_data['user_uuid'] = 'respondent.test'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'msg_to': 'test',
                       'msg_from': 'respondent.test',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': context.msg_id,
                       'collection_case': 'collection case1',
                       'reporting_unit': 'reporting case1',
                       'business_name': 'ABusiness',
                       'survey': 'survey'}


# Scenario: A user sends a previously saved draft
@given('a user retrieves a previously saved draft')
def step_impl_user_retrieves_draft(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)
    context.message = json.loads(get_draft.data)


@when('the draft is sent')
def step_impl_draft_is_sent(context):
    context.response = app.test_client().post(url, data=json.dumps(context.message), headers=headers)


#  Scenario: Send a draft which is a reply to another message

@given('a message is identified as a draft which is a reply to another message')
def step_impl_a_message_is_a_draft_reply(context):
    data.update({'msg_to': 'test',
                 'msg_from': 'respondent.test',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '25e9172c-62d9-4ff7-98ac-661300ae9446',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})

    token_data['user_uuid'] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'msg_to': 'test',
                       'msg_from': 'respondent.test',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': '25e9172c-62d9-4ff7-98ac-661300ae9446',
                       'collection_case': 'collection case1',
                       'reporting_unit': 'reporting case1',
                       'business_name': 'ABusiness',
                       'survey': 'survey'}


@then('thread_id is not the same as msg_id')
def step_impl_thread_id_and_msg_id_are_not_equal(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_not_equals(resp['thread_id'], resp['msg_id'])
    nose.tools.assert_equal(resp['thread_id'], '25e9172c-62d9-4ff7-98ac-661300ae9446')


# Scenario 3: Submit a message with a missing "To" field and receive a 400 error
@given("the 'To' field is empty")
def step_impl_to_field_empty(context):
    data['msg_to'] = ''


# Scenario 4: Submit a message with a missing "From" field and receive a 400 error
@given("the 'From' field is empty")
def step_impl_from_field_empty(context):
    data['msg_from'] = ''


# Scenario 5: Submit a message with a missing "Body" field and receive a 400 error
@given("the 'Body' field is empty")
def step_impl_body_field_empty(context):
    data['body'] = ''


# Scenario 6: Submit a message with a missing "Subject" field and receive a 400
@given("the 'Subject' field is empty")
def step_impl_subject_field_empty(context):
    data['subject'] = ""


# Scenario 7: Message sent without a thread id
@given("the 'Thread ID' field is empty")
def step_impl_thread_id_field_empty(context):
    before_scenario(context)
    data['thread_id'] = ''


# Scenario 8: Message sent with a msg_to too long
@given("the 'To' field exceeds max limit in size")
def step_impl_to_field_exceeds_max_limit(context):
    data['msg_to'] = "x" * (constants.MAX_TO_LEN+1)


# Scenario 9: Message sent with a msg_from too long
@given("the 'From' field exceeds max limit in size")
def step_impl_from_field_exceeds_max_limit(context):
    data['msg_from'] = "y" * (constants.MAX_FROM_LEN+1)


# Scenario 10: Message sent with an empty survey field return 400
@given('the survey field is empty')
def step_impl_survey_field_empty(context):
    data['survey'] = ''


# Scenario 11: Message sent with a msg_id not a valid draft returns 400
@given('a message contains a msg_id and is not a valid draft')
def step_impl_message_contains_msg_id_and_is_not_valid_draft(context):
    data.update({'msg_id': 'test123',
                 'msg_to': 'test',
                 'msg_from': 'respondent.test',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})


# Scenario 12: When a message with the label of "Draft" is sent and another user is trying to send the same message return a 409
@given('a draft message is posted')
def step_impl_draft_message_posted(context):
    if 'msg_id' in data:
        del data['msg_id']

    token_data['user_uuid'] = data['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    #get etag from response using context
    context.etag =  json.loads(context.post_draft.data)
    headers['Etag'] = context.etag

    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'msg_to': 'test',
                       'msg_from': 'respondent.test',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': '',
                       'collection_case': 'collection case1',
                       'reporting_unit': 'reporting case1',
                       'business_name': 'ABusiness',
                       'survey': 'survey'}
    token_data['user_uuid'] = context.message['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post(url, data=json.dumps(context.message), headers=headers)


@when('another user tries to send the same message')
def step_impl_another_user_sends_same_message(context):
    data.update({'msg_id': context.msg_id,
                 'msg_to': 'internal.000000',
                 'msg_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})

    data['subject'] = 'edited'
    headers['Etag'] = context.etag

    token_data['user_uuid'] = 'respondent.000000'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post(url.format(context.msg_id),
                                             data=json.dumps(data), headers=headers)


@then('is shown a 409 error status')
def step_impl_is_shown_404(context):
    nose.tools.assert_equal(context.response.status_code, 409)


# Scenario 13:  Scenario: A Etag is not present within the header
@given('a message is created')
def step_impl_message_is_created(context):
    context.msg = {  'msg_to': 'test',
                     'msg_from': 'respondent.test',
                     'subject': 'test',
                     'body': 'Test',
                     'thread_id': '',
                     'collection_case': 'collection case1',
                     'reporting_unit': 'reporting case1',
                     'business_name': 'ABusiness',
                     'survey': 'RSI'}


@when('the message is sent with no Etag')
def step_impl_message_sent_no_etag(context):
    if 'ETag' in headers:
        del headers['ETag']

    token_data['user_uuid'] = context.msg['msg_from']
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    context.response = app.test_client().post(url, data=json.dumps(context.msg), headers=headers)


# Common Steps: used in multiple scenarios


@when("the message is sent")
def step_implmessage_is_sent(context):
    token_data['user_uuid'] = data['msg_from']
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


@then('thread_id is the same as msg_id')
def step_impl_thread_id_and_msg_id_are_equal(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_equal(resp['thread_id'], resp['msg_id'])


@then("a 400 error status is returned")
def step_impl_400_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@then('a 201 status code is the response')
def step_impl_201_returned(context):
    nose.tools.assert_equal(context.response.status_code, 201)
