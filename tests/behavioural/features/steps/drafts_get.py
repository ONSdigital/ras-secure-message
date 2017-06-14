import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.repository import database
from flask import current_app, json
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings


url = "http://localhost:5050/drafts"
token_data = {
            "user_uuid": "respondent.2134",
            "role": "respondent"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collectioncase',
        'reporting_unit': 'AReportingUnit',
        'business_name': 'ABusiness',
        'survey': 'survey'}


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

#  Scenario: User requests list of drafts


@given('the user has created and saved multiple drafts')
def step_impl_user_has_created__and_saved_multiple_drafts(context):
    reset_db()
    data.update({'urn_to': 'test',
                 'urn_from': 'respondent.2134',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})
    for _ in range(0, 10):
        app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data), headers=headers)


@when("the user requests drafts")
def step_impl_user_requests_drafts(context):
    token_data['user_urn'] = 'respondent.2134'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}?limit={1}&page={2}'.format(url, 7, 1), headers=headers)


@then("only the users drafts are returned")
def step_impl_only_the_users_drafts_are_returned(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        nose.tools.assert_equal(response['messages'][x]['labels'], ['DRAFT'])
        nose.tools.assert_equal(response['messages'][x]['urn_from'], data['urn_from'])

    nose.tools.assert_equal(len(response['messages']), 7)


#   Scenario: User requests second page of list of drafts

@when("the user requests second page of drafts")
def step_impl_the_user_requests_second_page_of_drafts(context):
    token_data['user_urn'] = 'respondent.2134'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}?limit={1}&page={2}'.format(url, 7, 2), headers=headers)


@then("user will get drafts from second page of pagination")
def step_impl_user_will_get_drafts_from_second_page_of_pagination(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        nose.tools.assert_equal(response['messages'][x]['labels'], ['DRAFT'])
        nose.tools.assert_equal(response['messages'][x]['urn_from'], data['urn_from'])

    nose.tools.assert_equal(len(response['messages']), 3)

