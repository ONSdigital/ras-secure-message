from behave import given, when, then
from flask import current_app, json
from app.common.alerts import AlertUser, AlertViaGovNotify
from unittest import mock
from app.repository import database
from app.application import app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings
import nose
import uuid


url = "http://localhost:5050/draft/{0}"
token_data = {
            "user_uuid": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
            "role": "respondent"
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


# Scenario 1: User requests draft

@given('a user requests a valid draft')
def step_impl_user_requests_valid_draft(context):
    data.update({'msg_to': ['BRES'],
                 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
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


@then('the draft is returned')
def step_impl_assert_draft_is_returned(context):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(response['msg_id'], context.resp_data['msg_id'])


# Scenario 2: User requests draft that does not exist
@given('a user wants a draft that does not exist')
def step_impl_user_request_non_existent_draft(context):
    context.resp_data = dict(msg_id='')
    context.resp_data['msg_id'] = str(uuid.uuid4())


# Scenario 3: User requests draft not authorised to view
@given('a user is not authorised')
def step_impl_user_not_authorised(self, context):
    #   waiting for  authorisation to be implemented
    data.update({'msg_to': ['BRES'],
                 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'collection_exercise': 'collection exercise1',
                 'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                 'survey': 'BRES'})
    response = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(context.draft),
                                      headers=headers)
    context.resp_data = json.loads(response.data)


@then('the user is forbidden from viewing draft')
def step_impl_assert_403_returned(context):
    nose.tools.assert_equal(context.response.status_code, 403)


#   Scenario 4: User is retrieving the etag from the header
@given("there is a draft")
def step_impl_there_is_a_draft(context):
    data.update({'msg_to': ['BRES'],
                 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
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


# Common Steps: used in multiple scenarios
@when('the user requests the draft')
def step_impl_the_user_requests_draft(context):
    context.response = app.test_client().get(url.format(context.resp_data['msg_id']), headers=headers)
