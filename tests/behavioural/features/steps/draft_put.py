from behave import given, when,then
from app.application import app
from app.repository import database
from flask import current_app, json
import nose.tools
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings, constants

url = "http://localhost:5050/draft/{0}/modify"
token_data = {'user_urn': '00000000000'}
headers = {'Content-Type': 'application/json', 'Authorization': ''}


post_data = {'urn_to': 'internal.000000',
             'urn_from': 'respondent.000000',
             'subject': 'test',
             'body': 'Test',
             'thread_id': '2',
             'collection_case': 'collection case1',
             'reporting_unit': 'reporting case1',
             'survey': 'survey'}
data = {'urn_to': 'internal.000000',
        'urn_from': 'respondent.000000',
        'subject': 'test',
        'body': 'Test',
        'thread_id': '2',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'survey': 'survey'}

with app.app_context():
    database.db.init_app(current_app)
    database.db.drop_all()
    database.db.create_all()


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['Authorization'] = update_encrypted_jwt()


# Scenario 1: A user edits a previously saved draft
@given('a user edits a previously saved draft')
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)
    context.etag = get_draft.headers.get('ETag')
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['body'] = 'replaced'


@when('the user saves the draft')
def step_impl(context):
    if 'ETag' in headers:
        del headers['ETag']
    if hasattr(context, 'etag'):
        headers['ETag'] = context.etag
    context.response = app.test_client().put(url.format(context.msg_id), data=json.dumps(data), headers=headers)


@then('a success response is given')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 200)


# Scenario 2: A user edits a draft that has not been previously saved
@given('a user edits a non-existing draft')
def step_impl(context):
    data.update({'msg_id': '001',
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['body'] = 'replaced'
    context.msg_id = data['msg_id']


# Scenario 3: A user edits a draft that has a too large to attribute
@given("a user modifies a draft with a to attribute that is too big")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['urn_to'] = 'x' * (constants.MAX_TO_LEN+1)


# Scenario 4: A user edits a draft that has a too large from attribute
@given("a user modifies a draft with a from attribute that is too big")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['urn_from'] = 'x' * (constants.MAX_FROM_LEN+1)


# Scenario 5: A user edits a draft that has a too large body attribute
@given("a user modifies a draft with a body attribute that is too big")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['body'] = 'x' * (constants.MAX_BODY_LEN+1)


# Scenario 6: A user edits a draft that has a too large subject attribute
@given("a user modifies a draft with a subject attribute that is too big")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['subject'] = 'x' * (constants.MAX_SUBJECT_LEN+1)


# Scenario 7: A user edits a draft not including a to attribute
@given("a user modifies a draft not adding a to attribute")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)
    context.etag = get_draft.headers.get('ETag')
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['urn_to'] = ''


# Scenario 8: A user edits a draft not including a body attribute
@given("a user modifies a draft not adding a body attribute")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)
    context.etag = get_draft.headers.get('ETag')
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['body'] = ''


# Scenario 9: A user edits a draft not including a subject attribute
@given("a user modifies a draft not adding a subject attribute")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)
    context.etag = get_draft.headers.get('ETag')
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['subject'] = ''


# Scenario 10: A user edits a draft not including a subject attribute
@given("a user modifies a draft not adding a thread id attribute")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)
    context.etag = get_draft.headers.get('ETag')
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})
    data['thread_id'] = ''


# Scenario 11: A user edits a draft where msg id in url and in the message body do not match
@given("a user tries to modify a draft with mismatched msg ids")
def step_impl(context):
    add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data), headers=headers)
    post_resp = json.loads(add_draft.data)
    context.msg_id = post_resp['msg_id']
    data.update({'msg_id': '0000-0000-0000-0000',
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'Test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})


# Scenario 12: A user is editing a draft while another user tries to modify the same draft
@given("a draft message is being edited")
def step_impl(context):
        add_draft = app.test_client().post('http://localhost:5050/draft/save', data=json.dumps(post_data),
                                           headers=headers)
        post_resp = json.loads(add_draft.data)
        context.msg_id = post_resp['msg_id']
        get_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id),
                                          headers=headers)
        context.etag = get_draft.headers.get('ETag')
        data.update({'msg_id': context.msg_id,
                     'urn_to': 'internal.000000',
                     'urn_from': 'respondent.000000',
                     'subject': 'test',
                     'body': 'test',
                     'thread_id': '2',
                     'collection_case': 'collection case1',
                     'reporting_unit': 'reporting case1',
                     'survey': 'survey'})
        data['body'] = ''
        headers['Etag'] = context.etag
        context.response = app.test_client().put("http://localhost:5050/draft/{0}/modify".format(context.msg_id),
                                                 data=json.dumps(data), headers=headers)
        retrieved_draft = app.test_client().get('http://localhost:5050/draft/{0}'.format(context.msg_id), headers=headers)


@when("another user tries to modify the same draft message")
def step_impl(context):
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'survey': 'survey'})

    data['subject'] = 'edited'
    headers['Etag'] = context.etag
    context.response = app.test_client().put("http://localhost:5050/draft/{0}/modify".format(context.msg_id),
                                             data=json.dumps(data), headers=headers)


@then("a conflict error is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 409)
