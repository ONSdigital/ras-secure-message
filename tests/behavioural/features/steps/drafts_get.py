import flask
import nose.tools
from behave import given, then, when
from app.application import app
from flask import json
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings


url = "http://localhost:5050/drafts"
token_data = {
            "user_uuid": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
            "role": "respondent"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'msg_to': 'BRES',
        'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collectioncase',
        'reporting_unit': 'AReportingUnit',
        'business_name': 'ABusiness',
        'collection_exercise': 'collectionexercise',
        'survey': 'BRES'}



def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['Authorization'] = update_encrypted_jwt()

#  Scenario: User requests list of drafts


@given('the user has created and saved multiple drafts')
def step_impl_user_has_created__and_saved_multiple_drafts(context):
    data.update({'msg_to': 'BRES',
                 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'collection_exercise': 'collection exercise1',
                 'survey': 'BRES'})

    for _ in range(0, 10):
        app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data), headers=headers)


@when("the user requests drafts")
def step_impl_user_requests_drafts(context):
    token_data['user_urn'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}?limit={1}&page={2}'.format(url, 7, 1), headers=headers)


@then("only the users drafts are returned")
def step_impl_only_the_users_drafts_are_returned(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        nose.tools.assert_equal(response['messages'][x]['labels'], ['DRAFT'])
        nose.tools.assert_equal(response['messages'][x]['msg_from'], {"id": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882", "firstname": "Vana", "surname": "Oorschot", "email": "vana123@aol.com", "telephone": "+443069990289", "status": "ACTIVE"})

    nose.tools.assert_equal(len(response['messages']), 7)


#   Scenario: User requests second page of list of drafts

@when("the user requests second page of drafts")
def step_impl_the_user_requests_second_page_of_drafts(context):
    token_data['user_urn'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}?limit={1}&page={2}'.format(url, 7, 2), headers=headers)


@then("user will get drafts from second page of pagination")
def step_impl_user_will_get_drafts_from_second_page_of_pagination(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        nose.tools.assert_equal(response['messages'][x]['labels'], ['DRAFT'])
        nose.tools.assert_equal(response['messages'][x]['msg_from'], {"id": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882", "firstname": "Vana", "surname": "Oorschot", "email": "vana123@aol.com", "telephone": "+443069990289", "status": "ACTIVE"})

    nose.tools.assert_equal(len(response['messages']), 3)

