import nose
from behave import given, when, then
from flask import current_app, json
from app.common.alerts import AlertUser, AlertViaGovNotify
from unittest import mock
from app.repository import database
from app.application import app
from app import constants
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings


url = "http://localhost:5050/draft/save"
token_data = {
            "user_uuid": "BRES",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {}

AlertUser.alert_method = mock.Mock(AlertViaGovNotify)


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)


headers['Authorization'] = update_encrypted_jwt()

with app.app_context():
    database.db.init_app(current_app)
    database.db.drop_all()
    database.db.create_all()


# Scenario 1: Save a valid draft get a 201 return
@given('a valid draft')
def step_impl_valid_draft(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 2: Save a draft with body field empty return 201
@given('a draft has an body field set to empty')
def step_impl_draft_with_empty_body(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': '',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 3: Save a draft with a message ID will return 400
@given('a draft including a msg_id')
def step_impl_draft_with_msg_id(context):
    data.update({'msg_id': 'Amsgid',
                 'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 4: Save a draft with a to field too large return 400
@given('a draft with to field too large in size')
def step_impl_draft_with_to_field_too_large(context):
    data.update({'msg_to': ['x' * (constants.MAX_TO_LEN+1)],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 5: Save a draft with a from field too large return 400
@given('a draft with from field too large in size')
def step_impl_draft_with_from_field_too_large(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'x' * (constants.MAX_FROM_LEN+1),
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 6: Save a draft with a body field too large return 400
@given('a draft with body field too large in size')
def step_impl_draft_with_body_field_too_large(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'x' * (constants.MAX_BODY_LEN+1),
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 7: Save a draft with a subject field too large return 400
@given('a draft with subject field too large in size')
def step_impl_draft_with_subject_field_too_large(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'x' * (constants.MAX_SUBJECT_LEN+1),
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 8: Save a draft with an empty from field return 400
@given('a draft with a from field set as empty')
def step_impl_draft_with_empty_from_field(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': '',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 9: Save a draft with an empty survey field return 400
@given('a draft with a survey field set as empty')
def step_impl_draft_with_empty_survey_field(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': ''})


# Scenario 10: Save a draft with a collection case field too large return 400
@given('a draft with collection case field too large in size')
def step_impl_draft_with_collection_case_field_too_large(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'x' * (constants.MAX_COLLECTION_CASE_LEN+1),
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


# Scenario 11: Save a draft with a collection exercise field too large return 400
@given('a draft with collection exercise field too large in size')
def step_impl_draft_with_collection_exercise_field_too_large(context):
    data.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                 'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'x' * (constants.MAX_COLLECTION_EXERCISE_LEN+1),
                 'survey': 'survey'})


# Scenario 12: As a user I would like a new draft message not related to a thread to be given the message id as a thread id
@given('A user creates a draft that is not associated with a thread')
def step_impl_draft_message_withour_thread_id(context):
    data.pop('msg_id', 'Amsgid')
    data.update({'msg_from': 'BRES',
                 'subject': 'test',
                 'body': 'Test',
                 'collection_case': 'collection case1',
                 'ru_id': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'survey'})


@then('the thread id should be set to the message id')
def step_impl_thread_id_set_as_msg_id(context):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(response['msg_id'], response['thread_id'])


# Scenario 13: As a user the message id for my saved draft should be returned when saving a draft
@given("a user creates a valid draft")
def step_impl_user_creates_valid_draft(context):
    context.draft = {'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                     'msg_from': 'BRES',
                     'subject': 'test',
                     'body': 'Test',
                     'thread_id': '',
                     'collection_case': 'collection case1',
                     'ru_id': 'reporting case1',
                     'business_name': 'ABusiness',
                     'collection_exercise': 'collection exercise1',
                     'survey': 'RSI'}


@when("the user saves this draft")
def step_impl_user_saves_draft(context):
    context.response = app.test_client().post(url, data=json.dumps(context.draft), headers=headers)


@then("the message id should be returned in the response")
def step_implmsg_id_returned(context):
    resp_data = json.loads(context.response.data)
    nose.tools.assert_true(resp_data['msg_id'] is not None)


# Common Steps: used in multiple scenarios
@when('the draft is saved')
def step_impl_draft_is_saved(context):
    context.response = app.test_client().post(url, data=json.dumps(data), headers=headers)
