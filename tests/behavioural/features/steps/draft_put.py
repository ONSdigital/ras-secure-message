from behave import given, when,then
from app.application import app
from app.repository import database
from flask import current_app, json
import nose.tools
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings

url = "http://localhost:5050/draft/{0}"
token_data = {'user_urn': '00000000000'}
headers = {'Content-Type': 'application/json', 'authentication': ''}

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


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['authentication'] = update_encrypted_jwt()


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


