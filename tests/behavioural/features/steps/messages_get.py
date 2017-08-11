import flask
import nose.tools
from behave import given, then, when
from app.application import app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings, constants

url = "http://localhost:5050/messages"
token_data = {
            constants.USER_IDENTIFIER: "ce12b958-2a5f-44f4-a6da-861e59070a31",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}

data = {'msg_to': ['test'],
        'msg_from': 'ce12b958-2a5f-44f4-a6da-861e59070a31',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collectioncase',
        'collection_exercise': 'collectionexercise',
        'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
        'survey': constants.BRES_SURVEY}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)


headers['Authorization'] = update_encrypted_jwt()


# Scenario 1: Respondent sends multiple messages and retrieves the list of messages with their labels (see common code)
# Scenario 2: Internal user sends multiple messages and retrieves the list of messages with their labels (see common code)
# Scenario 3: Respondent sends multiple messages and internal user retrieves the list of messages with their labels (see common code)
# Scenario 4: Internal user sends multiple messages and Respondent retrieves the list of messages with their labels (see common code)
# Scenario 5: As an external user I would like to be able to view a list of messages
@given("an external user has multiple messages")
def step_impl_external_user_has_multiple_messages(context):
    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'

    headers['Authorization'] = update_encrypted_jwt()
    data['msg_from'] = constants.BRES_USER
    for x in range(0, 2):
        app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data), headers=headers)
        app.test_client().post("http://localhost:5050/draft/save", data=flask.json.dumps(data), headers=headers)


@when("the external user requests all messages")
def step_impl_external_user_requests_all_messages(context):
    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    request = app.test_client().get(url, headers=headers)
    context.response = flask.json.loads(request.data)


# Scenario 6: As an internal user I would like to be able to view a list of messages
@given("an internal user has multiple messages")
def step_impl_internal_user_has_multiple_messages(context):
    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    headers['Authorization'] = update_encrypted_jwt()
    data['msg_from'] = constants.BRES_USER
    for x in range(0, 2):
        app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data), headers=headers)
        app.test_client().post("http://localhost:5050/draft/save", data=flask.json.dumps(data), headers=headers)


@when("the internal user requests all messages")
def step_impl_internal_user_requests_all_messages(context):
    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    request = app.test_client().get(url, headers=headers)
    context.response = flask.json.loads(request.data)


# Scenario 7: Respondent and internal user sends multiple messages and Respondent retrieves the list of sent messages
@given('a respondent and an Internal user sends multiple messages')
def step_impl_respondant_and_internal_user_send_multiple_messages(context):

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)

    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = [constants.BRES_USER]
        data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
        token_data['user_uuid'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
        token_data['role'] = 'respondent'
        headers['Authorization'] = update_encrypted_jwt()
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their sent messages')
def step_impl_respondent_gets_their_sent_messages(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}{1}'.format(url, '?label=SENT'), headers=headers)


@then('the retrieved messages should all have sent labels')
def step_impl_the_retrieved_messaages_all_have_sent_labels(context):
    response = flask.json.loads(context.response.data)
    for x in range(1, len(response['messages'])):
        nose.tools.assert_equal(response['messages'][x]['labels'], ['SENT'])

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario 8: As a user I would like to be able to view a list of inbox messages
@given("a internal user receives multiple messages")
def step_impl_internal_user_receives_multiple_messages(context):

    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = [constants.BRES_USER]
        data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@given("a respondent user receives multiple messages")
def step_impl_respondent_receives_multiple_messages(context):

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when("the internal user gets their inbox messages")
def step_impl_internal_user_gets_their_inbox_messages(context):
    token_data[constants.USER_IDENTIFIER] = 'ce12b958-2a5f-44f4-a6da-861e59070a31'
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}{1}'.format(url, '?label=INBOX'), headers=headers)


@then("the retrieved messages should all have inbox labels")
def step_impl_assert_all_messages_have_inbox_and_unread_labels(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['messages'][1]['labels'], ['INBOX', 'UNREAD'])

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario 9: Respondent and internal user sends multiple messages and Respondent retrieves the list of messages with ru
@given('a Internal user sends multiple messages with different reporting unit')
def step_impl_internal_user_sends_multiple_messages_with_different_ru(context):

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        data['ru_id'] = '7fc0e8ab-189c-4794-b8f4-9f05a1db185b'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their messages with particular reporting unit')
def step_impl_respondent_gets_their_messages_with_particular_ru(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}{1}'.format(url, '?ru_id=7fc0e8ab-189c-4794-b8f4-9f05a1db185b'),
                                             headers=headers)


@then('the retrieved messages should have the correct reporting unit')
def step_impl_assert_correct_ru(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['messages'][1]['ru_id'], '7fc0e8ab-189c-4794-b8f4-9f05a1db185b')


# Scenario 10: Internal user sends multiple messages and Respondent retrieves the list of messages with particular survey
@given('a Internal user sends multiple messages with different survey')
def step_impl_internal_user_sends_multiple_messages_with_different_survey(context):

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        data['survey'] = 'AnotherSurvey'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their messages with particular survey')
def step_impl_respondent_gets_their_messages_with_particular_survey(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}{1}'.format(url, '?survey=BRES'), headers=headers)


@then('the retrieved messages should have the correct survey')
def step_impl_retrieved_messages_shoud_have_correct_survey(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['messages'][1]['survey'], constants.BRES_SURVEY)

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario 11: Internal user sends multiple messages and Respondent retrieves the list of messages with particular cc
@given('a Internal user sends multiple messages with different collection case')
def step_impl_internal_user_sends_multiple_messages_with_different_collection_case(context):

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        data['collection_case'] = 'AnotherCollectionCase'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their messages with particular collection case')
def step_impl_respondent_retrieves_messaegs_with_particular_collection_case(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}{1}'.format(url, '?cc=AnotherCollectionCase'), headers=headers)


@then('the retrieved messages should have the correct collection case')
def step_impl_assert_messages_have_correct_collection_case(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['messages'][1]['collection_case'], 'AnotherCollectionCase')

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario 12: Internal user sends multiple messages and Respondent retrieves the list of messages with particular ce
@given('a Internal user sends multiple messages with different collection exercise')
def step_impl_internal_user_sends_multiple_messages_with_different_collection_exercise(context):

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        data['collection_exercise'] = 'AnotherCollectionExercise'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their messages with particular collection exercise')
def step_impl_respondent_retrieves_messages_with_particular_collection_exercise(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}{1}'.format(url, '?ce=AnotherCollectionExercise'), headers=headers)


@then('the retrieved messages should have the correct collection exercise')
def step_impl_assert_messages_have_correct_collection_exercise(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['messages'][1]['collection_exercise'], 'AnotherCollectionExercise')

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario 13: Respondent creates multiple draft messages and Respondent retrieves the list of draft messages
@when('the Respondent gets their draft messages')
def step_impl(context):
    headers[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    context.response = app.test_client().get('{0}{1}'.format(url, '?label=DRAFT'), headers=headers)


@then('the retrieved messages should all have draft labels')
def step_impl_assert_all_messages_have_draft_labels(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['messages'][1]['labels'], ['DRAFT'])

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario 14: Respondent creates multiple draft messages and Internal user retrieves a list of messages
@then('the retrieved messages should not have DRAFT_INBOX labels')
def step_impl_assert_no_message_has_draft_inbox_label(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_equal(response['messages'][str(x)]['labels'], ['DRAFT'])
        nose.tools.assert_not_equal(response['messages'][str(x)]['labels'], ['DRAFT_INBOX'])


# Scenario 15: User provides parameters that are invalid
@given('parameter limit has value string')
def step_impl_parameter_limit_has_string_value(context):
    context.params = "?limit=string"


@given('parameter page has value string')
def step_impl_parameter_page_has_string_value(context):
    context.params = "?page=string"


@given('parameter survey has value NotASurvey')
def step_impl_parameter_survey_is_not_a_survey(context):
    context.params = "?survey=NotASurvey"


@given('parameter labels has value NotALabel')
def step_impl_parameter_label_has_value_not_a_label(context):
    context.params = "?labels=NotALabel"


# Scenario 16: User provides parameters that are too large
@given('parameter ru_id has value LongerThan11Chars')
def step_impl_ru_id_equals_longer_than_1_character(context):
    context.params = "?ru_id=LongerThan11Chars"


@given('parameter labels has value INBOX-SENT-ARCHIVED-DRAFT-INBOX-SENT-ARCHIVED-DRAFT')
def step_impl_labels_param_set_to_include_all(context):
    context.params = "?labels=INBOX-SENT-ARCHIVED-DRAFT-INBOX-SENT-ARCHIVED-DRAFT"


# Scenario 17: User gets messages with various labels options
@when('respondent gets messages with labels INBOX')
def step_impl_respondent_gets_message_with_label_inbox(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels=INBOX"
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@when('respondent gets messages with labels SENT')
def step_impl_respondent_gets_messages_with_label_sent(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels=SENT"
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@when('respondent gets messages with labels ARCHIVED')
def step_impl_respondent_gets_messages_with_label_archived(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels=ARCHIVED"
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@when('respondent gets messages with labels DRAFT')
def step_impl_respondent_gets_messages_with_label_draft(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels=DRAFT"
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@when('respondent gets messages with labels INBOX-SENT')
def step_impl_respondent_gets_messages_with_labels_inbox_sent(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels=INBOX-SENT"
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@when('respondent gets messages with labels INBOX-SENT-ARCHIVED')
def step_impl_respondent_gets_messages_with_labels_inbox_sent_archived(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels=INBOX-SENT-ARCHIVED"
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@when('respondent gets messages with labels INBOX-SENT-ARCHIVED-DRAFT')
def step_impl_respondent_gets_messages_with_labels_inbox_sent_archived_draft(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels=INBOX-SENT-ARCHIVED-DRAFT"
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@then('messages returned should have one of the labels INBOX')
def step_impl_assert_one_message_has_inbox_label(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_true('INBOX' in response['messages'][str(x)]['labels'])


@then('messages returned should have one of the labels SENT')
def step_impl_assert_one_message_has_label_sent(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_true('SENT' in response['messages'][x]['labels'])


@then('messages returned should have one of the labels ARCHIVED')
def step_impl_assert_one_message_has_label_archived(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_true('ARCHIVED' in response['messages'][x]['labels'])


@then('messages returned should have one of the labels DRAFT')
def step_impl_assert_one_message_has_label_draft(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_true('DRAFT' in response['messages'][x]['labels'])


@then('messages returned should have one of the labels INBOX-SENT')
def step_impl_assert_one_message_has_label_inbox_sent(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_true('INBOX' in response['messages'][x]['labels'] or
                               'SENT' in response['messages'][x]['labels'])


@then('messages returned should have one of the labels INBOX-SENT-ARCHIVED')
def step_impl_assert_one_message_has_label_sent_archived(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_true('INBOX' in response['messages'][x]['labels'] or
                               'SENT' in response['messages'][x]['labels'] or
                               'ARCHIVED' in response['messages'][x]['labels'])


@then('messages returned should have one of the labels INBOX-SENT-ARCHIVED-DRAFT')
def step_impl_assert_one_message_has_label_sent_draft(context):
    response = flask.json.loads(context.response.data)

    for x in range(1, len(response['messages'])):
        nose.tools.assert_true('INBOX' in response['messages'][1]['labels'] or
                               'SENT' in response['messages'][1]['labels'] or
                               'ARCHIVED' in response['messages'][1]['labels'] or
                               'DRAFT' in response['messages'][1]['labels'])


# Scenario 18: User gets messages with no labels options
@when('respondent gets messages with labels empty')
def step_impl_assert_messages_with_empty_labels(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    params = "?labels="
    url_with_param = "{0}{1}".format(url, params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@then('all messages should be returned')
def step_impl_assert_all_messages_returned(context):
    response = flask.json.loads(context.response.data)
    # change number to expected number of messages depending on the
    # "there are multiple messages to retrieve for all labels" step
    num = 3
    nose.tools.assert_equal(len(response['messages']), num)


# Common Steps: used in multiple scenarios
@given("a respondent sends multiple messages")
def step_impl_respondent_sends_multiple_messages(context):

    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = [constants.BRES_USER]
        data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
        token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
        token_data['role'] = 'respondent'
        headers['Authorization'] = update_encrypted_jwt()
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)


@given("a Internal user sends multiple messages")
def step_impl_internal_user_sends_multiple_messages(context):

    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()

    for x in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                                  headers=headers)


@given('a Respondent creates multiple draft messages')
def step_impl_respondent_creates_multiple_draft_messages(context):

    for x in range(0, 2):
        draft = {'msg_to': [constants.BRES_USER],
                 'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'collection_exercise': 'collection exercise1',
                 'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
                 'survey': constants.BRES_SURVEY}
        token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
        token_data['role'] = 'respondent'
        headers['Authorization'] = update_encrypted_jwt()
        context.response = app.test_client().post("http://localhost:5050/draft/save", data=flask.json.dumps(draft),
                                                  headers=headers)


@given('there are multiple messages to retrieve for all labels')
def step_impl_multiple_messages_for_all_labels(context):

    for _ in range(0, 2):
        data['msg_to'] = ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882']
        data['msg_from'] = constants.BRES_USER
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for _ in range(0, 2):
        data['msg_to'] = [constants.BRES_USER]
        data['msg_from'] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    # need to implement adding draft messages, archived messages and read messages for user 0a7ad740-10d5-4ecb-b7ca-3c0384afb882


@when('user gets messages using the parameters')
def step_impl_get_messages_using_params(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    headers['Authorization'] = update_encrypted_jwt()
    url_with_param = "{0}{1}".format(url, context.params)
    context.response = app.test_client().get(url_with_param, headers=headers)


@when("the respondent user gets their inbox messages")
def step_impl_assert_respondent_gets_their_inbox_messages(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get('{0}{1}'.format(url, '?label=INBOX'), headers=headers)


@when("the Internal user gets their messages")
def step_impl_internal_user_gets_their_messages(context):
    token_data[constants.USER_IDENTIFIER] = constants.BRES_USER
    token_data['role'] = 'internal'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url, headers=headers)


@when("the respondent gets their messages")
def step_impl_respondent_gets_their_messages(context):
    token_data[constants.USER_IDENTIFIER] = '0a7ad740-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url, headers=headers)


@when("A different external user requests all messages")
def step_impl_respondent_gets_their_messages(context):
    token_data[constants.USER_IDENTIFIER] = 'someonee-10d5-4ecb-b7ca-3c0384afb882'
    token_data['role'] = 'respondent'
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(url, headers=headers)


@then("the retrieved messages should have the correct SENT labels")
def step_impl_retrieved_messages_should_have_sent_labels(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        nose.tools.assert_equal(response['messages'][x]['labels'], ['SENT'])


@then("the retrieved messages should have the correct INBOX and UNREAD labels")
def step_impl_message_should_have_correct_inbox_and_unread_labels(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        # num = x+1
        nose.tools.assert_equal(response['messages'][x]['labels'], ['INBOX', 'UNREAD'])
        nose.tools.assert_true(len(response['messages'][x]['labels']), 2)
        nose.tools.assert_true('INBOX' in response['messages'][x]['labels'])
        nose.tools.assert_true('UNREAD' in response['messages'][x]['labels'])


@then("all of that users messages are returned")
def step_impl_assert_correct_number_of_messages_returned(context):
    nose.tools.assert_equal(len(context.response['messages']), 4)


@then('No messages should be returned')
def step_impl_no_messages_returned(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(len(response['messages']), 0)
