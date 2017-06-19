import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings
import uuid

url = "http://localhost:5050/thread/{0}"
token_data = {
            "user_uuid": "000000000",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'msg_to': 'test',
        'msg_from': 'test',
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

# Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation


@given("a respondent and internal user have a conversation")
def step_impl_respondent_and_internal_user_hav_a_conversation(context):

    data['thread_id'] = 'AConversation'
    for _ in range(0, 2):
        token_data['user_uuid'] = 'respondent.122342'
        token_data['role'] = 'respondent'
        headers['Authorization'] = update_encrypted_jwt()

        data['msg_to'] = 'BRES'
        data['msg_from'] = 'respondent.122342'
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)
        token_data['user_uuid'] = 'BRES'
        token_data['role'] = 'internal'
        headers['Authorization'] = update_encrypted_jwt()

        data['msg_to'] = 'respondent.122342'
        data['msg_from'] = 'BRES'
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)


@when("the respondent gets this conversation")
def step_impl_respondent_gets_conversation(context):
    token_data['user_uuid'] = 'respondent.122342'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(data['thread_id']), headers=headers)


@then("all messages from that conversation should be received")
def step_impl_assert_all_messages_in_conversation_are_received(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(len(response), 4)


#   Scenario: Respondent and internal user have a conversation and respondent retrieves the conversation

@when("the internal user gets this conversation")
def step_impl_internal_user_gets_conversation(context):
    token_data['user_uuid'] = 'BRES'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url.format(data['thread_id']), headers=headers)

#   Scenario: Respondent and internal user have a conversation, including a draft, and respondent retrieves the conversation


@given("internal user creates a draft")
def step_impl_internal_user_creates_a_draft(context):
    token_data['user_uuid'] = 'BRES'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    data['msg_to'] = 'respondent.122342'
    data['msg_from'] = 'BRES'
    data['thread_id'] = 'AConversation'
    context.response = app.test_client().post("http://localhost:5050/draft/save", data=flask.json.dumps(data),
                                              headers=headers)

#   Scenario: Respondent and internal user have a conversation, including a draft, and internal user retrieves the conversation


@then("all messages from that conversation should be received including draft")
def step_impl_assert_all_messages_from_conversation_are_received(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(len(response), 5)


#   Scenario: Respondent and internal user have a conversation and internal user retrieves that conversation from multiple conversations
@given("internal user has multiple conversations")
def step_impl_internal_user_has_multiple_conversations(context):

    for _ in range(0, 2):
        data['thread_id'] = str(uuid.uuid4())
        data['msg_to'] = 'BRES'
        data['msg_from'] = 'respondent.122342'
        token_data['user_uuid'] = 'respondent.122342'
        token_data['role'] = 'respondent'
        headers['Authorization'] = update_encrypted_jwt()
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)
        data['msg_to'] = 'respondent.122342'
        data['msg_from'] = 'BRES'
        token_data['user_uuid'] = 'BRES'
        token_data['role'] = 'internal'
        headers['Authorization'] = update_encrypted_jwt()
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)
    data['thread_id'] = 'AConversation'


#   Scenario: User tries to retrieve a conversation that does not exist
@given("a respondent picks a conversation that does not exist")
def step_impl_pick_conversation_that_does_not_exist(context):
    data['thread_id'] = str(uuid.uuid4())
