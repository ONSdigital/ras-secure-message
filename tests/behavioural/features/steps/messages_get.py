import flask
import nose.tools
from behave import given, then, when
from app.application import app
import uuid
from app.repository import database
from flask import current_app

url = "http://localhost:5050/messages"
headers = {'Content-Type': 'application/json', 'user_urn': ''}

data = {'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collectioncase',
        'reporting_unit': 'AReportingUnit',
        'survey': 'survey'}


def reset_db():
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()


def before_scenario(context, scenario):
    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")
        return

# Scenario: Respondent sends multiple messages and retrieves the list of messages with their labels


@given("a respondent sends multiple messages")
def step_impl(context):
    reset_db()
    for x in range(0, 2):
        data['urn_to'] = 'internal.12344'
        data['urn_from'] = 'respondent.122342'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                              data=flask.json.dumps(data), headers=headers)


@when("the respondent gets their messages")
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get(url, headers=headers)


@then("the retrieved messages should have the correct SENT labels")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        num = x+1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['SENT'])


# Scenario: Internal user sends multiple messages and retrieves the list of messages with their labels

@given("a Internal user sends multiple messages")
def step_impl(context):
    reset_db()
    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                              data=flask.json.dumps(data), headers=headers)


@when("the Internal user gets their messages")
def step_impl(context):
    headers['user_urn'] = 'internal.122342'
    context.response = app.test_client().get(url, headers=headers)

# Scenario: Respondent sends multiple messages and internal user retrieves the list of messages with their labels
# Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with their labels


@then("the retrieved messages should have the correct INBOX and UNREAD labels")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        num = x+1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['INBOX', 'UNREAD'])
        nose.tools.assert_true(len(response['messages'][str(num)]['labels']), 2)
        nose.tools.assert_true('INBOX' in response['messages'][str(num)]['labels'])
        nose.tools.assert_true('UNREAD' in response['messages'][str(num)]['labels'])

# Scenario: As an external user I would like to be able to view a lst of messages


@given("multiple messages have been sent to an external user")
def step_impl(context):
    for x in range(0, 2):
        data['urn_to'] = 'respondent.123'
        app.test_client().post("http://localhost:5050/message/send", headers=headers)


@when("the external user navigates to their messages")
def step_impl(context):
    headers['user_urn'] = 'respondent.123'
    context.response = app.test_client().get(url, headers=headers)


@then("messages are displayed")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true(len(response['messages']), 2)

# Scenario: Respondent and internal user sends multiple messages and Respondent retrieves the list of sent messages


@given('a respondent and an Internal user sends multiple messages')
def step_impl(context):
    reset_db()
    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for x in range(0, 2):
        data['urn_to'] = 'internal.12344'
        data['urn_from'] = 'respondent.122342'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their sent messages')
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get('{0}{1}'.format(url, '?label=SENT'), headers=headers)


@then('the retrieved messages should all have sent labels')
def step_impl(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        num = x + 1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['SENT'])

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario: Respondent and internal user sends multiple messages and Respondent retrieves the list of messages with ru


@given('a Internal user sends multiple messages with different reporting unit')
def step_impl(context):
    reset_db()

    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        data['reporting_unit'] = 'AnotherReportingUnit'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their messages with particular reporting unit')
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get('{0}{1}'.format(url, '?ru=AnotherReportingUnit'), headers=headers)


@then('the retrieved messages should have the correct reporting unit')
def step_impl(context):
    response = flask.json.loads(context.response.data)

    for x in range(0, len(response['messages'])):
        num = x + 1
        nose.tools.assert_equal(response['messages'][str(num)]['reporting_unit'], 'AnotherReportingUnit')

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with particular survey

@given('a Internal user sends multiple messages with different survey')
def step_impl(context):
    reset_db()

    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        data['survey'] = 'AnotherSurvey'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their messages with particular survey')
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get('{0}{1}'.format(url, '?survey=AnotherSurvey'), headers=headers)


@then('the retrieved messages should have the correct survey')
def step_impl(context):
    response = flask.json.loads(context.response.data)

    for x in range(0, len(response['messages'])):
        num = x + 1
        nose.tools.assert_equal(response['messages'][str(num)]['survey'], 'AnotherSurvey')

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario: Internal user sends multiple messages and Respondent retrieves the list of messages with particular cc


@given('a Internal user sends multiple messages with different collection case')
def step_impl(context):
    reset_db()

    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)
    for x in range(0, 2):
        data['urn_to'] = 'respondent.122342'
        data['urn_from'] = 'internal.12344'
        data['collection_case'] = 'AnotherCollectionCase'
        context.response = app.test_client().post("http://localhost:5050/message/send",
                                                  data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their messages with particular collection case')
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get('{0}{1}'.format(url, '?cc=AnotherCollectionCase'), headers=headers)


@then('the retrieved messages should have the correct collection case')
def step_impl(context):
    response = flask.json.loads(context.response.data)

    for x in range(0, len(response['messages'])):
        num = x + 1
        nose.tools.assert_equal(response['messages'][str(num)]['collection_case'], 'AnotherCollectionCase')

    nose.tools.assert_equal(len(response['messages']), 2)


# Scenario: Respondent creates multiple draft messages and Respondent retrieves the list of draft messages


@given('a Respondent creates multiple draft messages')
def step_impl(context):
    reset_db()

    for x in range(0, 2):
        draft = {'urn_to': 'internal.12344',
                 'urn_from': 'respondent.122342',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'}
        context.response = app.test_client().post("http://localhost:5050/draft/save", data=flask.json.dumps(data), headers=headers)


@when('the Respondent gets their draft messages')
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get('{0}{1}'.format(url, '?label=DRAFT'), headers=headers)


@then('the retrieved messages should all have draft labels')
def step_impl(context):
    response = flask.json.loads(context.response.data)

    for x in range(0, len(response['messages'])):
        num = x + 1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['DRAFT'])

    nose.tools.assert_equal(len(response['messages']), 2)

# Scenario: Respondent creates multiple draft messages and Internal user retrieves a list of messages


@then('the retrieved messages should not have DRAFT_INBOX labels')
def step_impl(context):
    response = flask.json.loads(context.response.data)

    for x in range(0, len(response['messages'])):
        num = x + 1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['DRAFT'])
        nose.tools.assert_not_equal(response['messages'][str(num)]['labels'], ['DRAFT_INBOX'])

    # nose.tools.assert_equal(len(response['messages']), 2)

# Respondent and internal user sends multiple messages and Respondent retrieves the list of inbox messages


@when('the Respondent gets their inbox messages')
def step_impl(context):
    headers['user_urn'] = 'respondent.122342'
    context.response = app.test_client().get('{0}{1}'.format(url, '?label=INBOX'), headers=headers)


@then('the retrieved messages should all have inbox labels')
def step_impl(context):
    response = flask.json.loads(context.response.data)
    for x in range(0, len(response['messages'])):
        num = x + 1
        nose.tools.assert_equal(response['messages'][str(num)]['labels'], ['INBOX', 'UNREAD'])

    nose.tools.assert_equal(len(response['messages']), 2)
