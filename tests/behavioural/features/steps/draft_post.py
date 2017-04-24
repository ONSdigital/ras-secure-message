from behave import given, when
from flask import current_app, json
from app.common.alerts import AlertUser, AlertViaGovNotify
from unittest import mock
from app.repository import database
from app.application import app
from app import constants

url = "http://localhost:5050/draft/save"
headers = {'Content-Type': 'application/json', 'user-urn': '000000000'}

data = {}

AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

with app.app_context():
    database.db.init_app(current_app)
    database.db.drop_all()
    database.db.create_all()


# Scenario 1: Save a valid draft get a 201 return
@given('a valid draft')
def step_impl(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 2: Save a draft with body field empty return 201
@given('a draft has an body field set to empty')
def step_impl(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': '',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 3: Save a draft with a message ID will return 400
@given('a draft including a msg_id')
def step_impl(context):
    data.update({'msg_id': 'Amsgid',
                 'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 4: Save a draft with a to field too large return 400
@given('a draft with to field too large in size')
def step_impl(context):
    data.update({'urn_to': 'x' * (constants.MAX_TO_LEN+1),
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 5: Save a draft with a from field too large return 400
@given('a draft with from field too large in size')
def step_impl(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'x' * (constants.MAX_FROM_LEN+1),
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 6: Save a draft with a body field too large return 400
@given('a draft with body field too large in size')
def step_impl(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'x' * (constants.MAX_BODY_LEN+1),
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 7: Save a draft with a subject field too large return 400
@given('a draft with subject field too large in size')
def step_impl(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'x' * (constants.MAX_SUBJECT_LEN+1),
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 8: Save a draft with an empty from field return 400
@given('a draft with a from field set as empty')
def step_impl(context):
    data.update({'urn_to': 'test',
                 'urn_from': '',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 9: Save a draft with an empty survey field return 400
@given('a draft with a survey field set as empty')
def step_impl(context):
    data.update({'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': ''})


# Common
@when('the draft is saved')
def step_impl(context):
    context.response = app.test_client().post(url, data=json.dumps(data), headers=headers)
