from behave import given, when,then
from app.application import app
from app.repository import database
from flask import current_app, json
import nose.tools

url = "http://localhost:5050/draft/{0}"
headers = {'Content-Type': 'application/json', 'user_urn': '00000000000'}

data = {'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'test',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'survey': 'survey'}
with app.app_context():
    database.db.init_app(current_app)
    database.db.drop_all()
    database.db.create_all()


# Scenario 1: An existing draft is updated 200 is returned
@given('a valid draft has been modified')
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['body'] = 'replaced'


@when('it is saved')
def step_impl(context):
    context.response = app.test_client().put(url.format(context.msg_id), data=json.dumps(data), headers=headers)


@then('a 200 is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 200)


# Scenario 2: A new draft is updated
@given('a non-existing draft is modified')
def step_impl(context):
    data.update({'msg_id': '001',
                 'urn_to': 'test',
                 'urn_from': 'test',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['body'] = 'replaced'
    context.msg_id = data['msg_id']


# Scenario 3: As an internal user I want to be able to edit a message from my drafts
@given("an internal user has opened a previously saved draft message")
def step_impl(context):
    data['urn_from'] = 'internal.123'
    response = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the internal user edits the content of the message and saves it as a draft")
def step_impl(context):
    data['subject'] = 'replaced'
    data['msg_id'] = context.msg_id
    app.test_client().put(url.format(context.msg_id), data=json.dumps(data), headers=headers)


@then("the original draft message is replaced by the edited version")
def step_impl(context):
    draft_get = app.test_client().get("http://localhost:5050/draft/{0}".format(context.msg_id), headers=headers)
    draft_data = json.loads(draft_get)
    nose.tools.assert_equal(draft_data['subject'], data['subject'])


# Scenario 4: As an External user I would like to be able to edit a message from drafts
@given("an external user has opened a previously saved draft message")
def step_impl(context):
    data['urn_from'] = 'respondent.123'
    response = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(data), headers=headers)
    resp_data = json.loads(response.data)
    context.msg_id = resp_data['msg_id']


@when("the external user edits the content of the message and saves it as a draft")
def step_impl(context):
    data['subject'] = 'replaced1'
    data['msg_id'] = context.msg_id
    app.test_client().put(url.format(context.msg_id), data=json.dumps(data), headers=headers)



