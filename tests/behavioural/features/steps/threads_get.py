import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings, constants

url = "http://localhost:5050/threads"
token_data = {
            constants.USER_IDENTIFIER: "000000000",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
        'msg_from': constants.BRES_USER,
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': 'AConversation',
        'collection_case': 'collectioncase',
        'collection_exercise': 'collectionexercise',
        'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
        'survey': constants.BRES_SURVEY}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)


headers['Authorization'] = update_encrypted_jwt()


# Scenario 1: Respondent and internal user have multiple conversations and respondent retrieves all conversation (see common steps)
# Scenario 2: Respondent and internal user have multiple conversations, including a draft, and respondent retrieves all conversation (see common steps)
# Scenario 3: Respondent and internal user have multiple conversations and internal user retrieves all conversation (see common steps)
# Scenario 4: Respondent and internal user have multiple conversations, including a draft, and internal user retrieves all conversation
@then("most recent message from each conversation is returned including draft")
def step_impl_most_recent_message_from_each_conversation_returned_with_draft(context):
    response = flask.json.loads(context.response.data)
    context.most_recent_messages[-1] = context.draft_id
    nose.tools.assert_equal(len(response['messages']), len(context.most_recent_messages))

    returned_messages = []

    for message in response['messages']:
        returned_messages.append(message['msg_id'])

    returned_messages.sort()
    context.most_recent_messages.sort()

    nose.tools.assert_equal(returned_messages, context.most_recent_messages)


# Common Steps: used in multiple scenarios
@given("a respondent and internal user have multiple conversations")
def step_impl_respondent_and_internal_user_hav_multiple_conversations(context):
    context.most_recent_messages = []

    for x in range(0, 3):
        data['thread_id'] = 'AConversation{0}'.format(x)
        for y in range(0, 2):
            token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
            token_data['role'] = 'respondent'
            headers['Authorization'] = update_encrypted_jwt()

            data['msg_to'] = ['internal.12344']
            data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
            context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                      headers=headers)

            token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
            token_data['role'] = 'internal'
            headers['Authorization'] = update_encrypted_jwt()

            data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
            data['msg_from'] = constants.BRES_USER
            context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                      headers=headers)

        context.most_recent_messages.append(flask.json.loads(context.response.data)['msg_id'])


@given("internal user has conversation with a draft")
def step_impl_internal_user_has_conversation_with_draft(context):

    data['thread_id'] = 'AnotherConversation'

    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    data['msg_to'] = [constants.BRES_USER]
    data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                              headers=headers)

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
    data['msg_from'] = constants.BRES_USER
    context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                              headers=headers)

    context.most_recent_messages.append(flask.json.loads(context.response.data)['msg_id'])

    data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
    data['msg_from'] = constants.BRES_USER
    context.response = app.test_client().post("http://localhost:5050/draft/save", data=flask.json.dumps(data),
                                              headers=headers)
    context.draft_id = flask.json.loads(context.response.data)['msg_id']


@when("the respondent gets all conversations")
def step_impl_respondent_gets_all_conversations(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url, headers=headers)


@when("the internal user gets all conversations")
def step_impl_internal_user_gets_all_conversations(context):
    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url, headers=headers)


@then("most recent message from each conversation is returned")
def step_impl_most_recent_message_from_each_conversation_returned(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(len(response['messages']), len(context.most_recent_messages))

    returned_messages = []

    for message in response['messages']:
        returned_messages.append(message['msg_id'])

    returned_messages.sort()
    context.most_recent_messages.sort()

    nose.tools.assert_equal(returned_messages, context.most_recent_messages)
