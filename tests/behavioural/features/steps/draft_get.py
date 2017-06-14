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
            "user_uuid": "respondent.2134",
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


#   Scenario: User requests draft

@given('a user requests a valid draft')
def step_impl_user_requests_valid_draft(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})
    response = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                      headers=headers)
    context.resp_data = json.loads(response.data)


@then('the draft is returned')
def step_impl_assert_draft_is_retuned(context):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(response['msg_id'], context.resp_data['msg_id'])


@then('a success response is returned')
def step_impl_assert_200_returned(context):
    nose.tools.assert_equal(context.response.status_code, 200)


#   Scenario: User requests draft that does not exist

@given('a user wants a draft that does not exist')
def step_impl_user_request_non_existant_draft(context):
    context.resp_data = dict(msg_id='')
    context.resp_data['msg_id'] = str(uuid.uuid4())


@then('the user receives a draft not found response')
def step_impl_assert_404_returned(context):
    nose.tools.assert_equal(context.response.status_code, 404)


#   Scenario: User requests draft not authorised to view

@given('a user is not authorised')
def step_impl_user_not_authorised(self, context):
    #   waiting for  authorisation to be implemented
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})
    response = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(context.draft),
                                      headers=headers)
    context.resp_data = json.loads(response.data)


@then('the user is forbidden from viewing draft')
def step_impl_assert_403_returned(context):
    nose.tools.assert_equal(context.response.status_code, 403)


#   Scenario: User is retrieving the etag from the header
@given("there is a draft")
def step_impl_there_is_a_draft(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})
    response = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                      headers=headers)
    context.resp_data = json.loads(response.data)


@then("an etag should be sent with the draft")
def step_impl_etag_should_be_sent_with_draft(context):
    etag = context.response.headers.get('ETag')
    nose.tools.assert_is_not_none(etag)
    nose.tools.assert_true(len(etag) == 40)


#   common
@when('the user requests the draft')
def step_impl_the_user_requests_draft(context):
    context.response = app.test_client().get(url.format(context.resp_data['msg_id']), headers=headers)
