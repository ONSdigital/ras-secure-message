import flask
import nose.tools
from behave import given, then, when
from app import constants
from app.application import app
from app.repository import database
from flask import current_app
from unittest import mock
from app.common.alerts import AlertUser, AlertViaGovNotify

url = "http://localhost:5050/message/send"
headers = {'Content-Type': 'application/json', 'user-urn': '0000000000'}
data = {}


def before_scenario(context):
    AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()

    data.update({'msg_id': '',
                 'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 1: Submitting a valid message and receiving a 201
@given('a valid message')
def step_impl(context):
    before_scenario(context)


# Scenario 2: Submit a message with a missing "To" field and receive a 400 error
@given("the 'To' field is empty")
def step_impl(context):
    data['urn_to'] = ''


# Scenario 3: Submit a message with a missing "From" field and receive a 400 error
@given("the 'From' field is empty")
def step_impl(context):
    data['urn_from'] = ''


# Scenario 4: Submit a message with a missing "Body" field and receive a 400 error
@given("the 'Body' field is empty")
def step_impl(context):
    data['body'] = ''


# Scenario 5: Submit a message with a missing "Subject" field and receive a 400
@given("the 'Subject' field is empty")
def step_impl(context):
    data['subject'] = ""


# Scenario 6: Message sent without a thread id
@given("the 'Thread ID' field is empty")
def step_impl(context):
    before_scenario(context)


# Scenario 7: Message sent with a urn_to too long
@given("the 'To' field exceeds max limit in size")
def step_impl(context):
    data['urn_to'] = "x" * (constants.MAX_TO_LEN+1)


# Scenario 8: Message sent with a urn_from too long
@given("the 'From' field exceeds max limit in size")
def step_impl(context):
    data['urn_from'] = "y" * (constants.MAX_FROM_LEN+1)


# Common Steps: used in multiple scenarios


@when("the message is sent")
def step_impl(context):
    context.response = app.test_client().post(url, data=flask.json.dumps(data), headers=headers)


@then("a 400 error status is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@then('a 201 status code is the response')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 201)
