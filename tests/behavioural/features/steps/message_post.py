import flask
import nose.tools
from behave import given, then, when
from app import application, constants
from unittest import mock
from app.common.alerts import AlertUser, AlertViaGovNotify

url = "http://localhost:5050/message/send"
headers = {'Content-Type': 'application/json', 'user-urn': '0000000000'}
data = {}


def before_scenario(context):
    AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

    data.update({'msg_id': '',
                 'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


@given('a valid message')
def step_impl(context):
    before_scenario(context)


@when('it is sent')
def step_impl(context):
    context.response = application.app.test_client().post(url, data=flask.json.dumps(data), headers=headers)


@then('a 201 HTTP response is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 201)


@given('a message with an empty "To" field')
def step_impl(context):
    data['urn_to'] = ''


@then('a 400 HTTP response is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@given('a message with an empty "From" field')
def step_impl(context):
    data['urn_from'] = ''


@then('a 400 HTTP response is returned as the response afterwards')
def step_impl(context):
    context.execute_steps("then a 400 HTTP response is returned")


@given('a message with an empty "Body" field')
def step_impl(context):
    data['body'] = ''


@then('a 400 HTTP response is returned as a response after')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@given('a message with an empty "Subject" field')
def step_impl(context):
    data['subject'] = ""


@then('a 400 HTTP response is returned as a response')
def step_impl(context):
    context.execute_steps('then a 400 HTTP response is returned as a response after')


@given('a message is sent with an empty "Thread ID"')
def step_impl(context):
    before_scenario(context)


@then('a 201 status code is the response')
def step_impl(context):
    print(context.response.data)
    nose.tools.assert_equal(context.response.status_code, 201)


# Scenario: Message sent with a urn_to too long

@given("a message is sent with a urn_to which exceeds the max limit")
def step_impl(context):
    data['urn_to'] = "x" * (constants.MAX_TO_LEN+1)


@when("the message is sent")
def step_impl(context):
    context.response = application.app.test_client().post(url, data=flask.json.dumps(data), headers=headers)


@then("a 400 error status is given")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


# Scenario: Message sent with a urn_from too long


@given("a message is sent with a urn_from which exceeds the field length")
def step_impl(context):
    data['urn_from'] = "y" * (constants.MAX_FROM_LEN+1)


@when("a message is sent")
def step_impl(context):
    context.response = application.app.test_client().post(url, data=flask.json.dumps(data), headers=headers)


@then("a 400 error is given")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)
