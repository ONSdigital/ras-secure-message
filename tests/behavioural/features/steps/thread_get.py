import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.repository import database
from flask import current_app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings
import uuid

url = "http://localhost:5050/thread/{0}"
token_data = {
            "user_urn": "000000000"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': 'AConversation',
        'collection_case': 'collectioncase',
        'reporting_unit': 'AReportingUnit',
        'business_name': 'ABusiness',
        'survey': 'BRES'}


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

# Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation


@given("a respondent and internal user have a conversation")
def step_impl(context):
    reset_db()

    data['thread_id'] = 'AConversation'
    for _ in range(0, 2):
        data['urn_to'] = 'internal.12344'
        data['urn_from'] = 'respondent.122342'
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)


@when("the respondent gets this conversation")
def step_impl(context):
    token_data['user_urn'] = 'respondent.122342'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(data['thread_id']), headers=headers)


@then("all messages from that conversation should be received")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(len(response), 4)


#   Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation

@when("the internal user gets this conversation")
def step_impl(context):
    token_data['user_urn'] = 'internal.12344'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(data['thread_id']), headers=headers)

#   Scenario: Respondent and internal user have a conversation, including a draft, and respondent retrieves the conversation


@given("internal user creates a draft")
def step_impl(context):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        data['thread_id'] = 'AConversation'
        context.response = app.test_client().post("http://localhost:5050/draft/save", data=flask.json.dumps(data),
                                                  headers=headers)

#   Scenario: Respondent and internal user have a conversation, including a draft, and internal user retrieves the conversation


@then("all messages from that conversation should be received including draft")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(len(response), 5)


#   Scenario: Respondent and internal user have a conversation and internal user retrieves that conversation from multiple conversations
@given("internal user has multiple conversations")
def step_impl(context):

    for _ in range(0, 2):
        data['thread_id'] = str(uuid.uuid4())
        data['urn_to'] = 'internal.12344'
        data['urn_from'] = 'respondent.122342'
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)
    data['thread_id'] = 'AConversation'


#   Scenario: User tries to retrieve a conversation that does not exist
@given("a respondent picks a conversation that does not exist")
def step_impl(context):
    reset_db()
    data['thread_id'] = str(uuid.uuid4())
