from flask import json
import nose.tools
from behave import given, then, when
from app import constants
from app.application import app
from app.repository import database
from flask import current_app
from unittest import mock
from app.common.alerts import AlertUser, AlertViaGovNotify
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings


url = "http://localhost:5050/message/send"
token_data = {
            "user_urn": "000000000"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}
data = {}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['Authorization'] = update_encrypted_jwt()


def before_scenario(context):
    AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()


    data.update({
                 'urn_to': 'test',
                 'urn_from': 'respondent.test',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})


# Scenario 1: Submitting a valid message and receiving a 201
@given('a valid message')
def step_impl(context):
    before_scenario(context)


# Scenario 2: Send a draft and receive a 201
@given('a message is identified as a draft')
def step_impl(context):
    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'urn_to': 'test',
                       'urn_from': 'respondent.test',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': '',
                       'collection_case': 'collection case1',
                       'reporting_unit': 'reporting case1',
                       'business_name': 'ABusiness',
                       'survey': 'survey'}


@when('the draft is sent')
def step_impl(context):
    context.response = app.test_client().post(url, data=json.dumps(context.message), headers=headers)


# Scenario 3: Submit a message with a missing "To" field and receive a 400 error
@given("the 'To' field is empty")
def step_impl(context):
    data['urn_to'] = ''


# Scenario 4: Submit a message with a missing "From" field and receive a 400 error
@given("the 'From' field is empty")
def step_impl(context):
    data['urn_from'] = ''


# Scenario 5: Submit a message with a missing "Body" field and receive a 400 error
@given("the 'Body' field is empty")
def step_impl(context):
    data['body'] = ''


# Scenario 6: Submit a message with a missing "Subject" field and receive a 400
@given("the 'Subject' field is empty")
def step_impl(context):
    data['subject'] = ""


# Scenario 7: Message sent without a thread id
@given("the 'Thread ID' field is empty")
def step_impl(context):
    before_scenario(context)
    data['thread_id'] = ''


# Scenario 8: Message sent with a urn_to too long
@given("the 'To' field exceeds max limit in size")
def step_impl(context):
    data['urn_to'] = "x" * (constants.MAX_TO_LEN+1)


# Scenario 9: Message sent with a urn_from too long
@given("the 'From' field exceeds max limit in size")
def step_impl(context):
    data['urn_from'] = "y" * (constants.MAX_FROM_LEN+1)


# Scenario 10: Message sent with an empty survey field return 400
@given('the survey field is empty')
def step_impl(context):
    data['survey'] = ''


# Scenario 11: Message sent with a msg_id not a valid draft returns 400
@given('a message contains a msg_id and is not a valid draft')
def step_impl(context):
    data.update({'msg_id': 'test123',
                 'urn_to': 'test',
                 'urn_from': 'respondent.test',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread_id': '',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})


# Scenario 12: When a message with the label of "Draft" is sent and another user is trying to send the same message return a 409
@given('a draft message is posted')
def step_impl(context):
    if 'msg_id' in data:
        del data['msg_id']

    context.post_draft = app.test_client().post("http://localhost:5050/draft/save", data=json.dumps(data),
                                                headers=headers)
    #get etag from response using context
    context.etag =  json.loads(context.post_draft.data)
    headers['Etag'] = context.etag

    msg_resp = json.loads(context.post_draft.data)
    context.msg_id = msg_resp['msg_id']
    context.message = {'msg_id': context.msg_id,
                       'urn_to': 'test',
                       'urn_from': 'respondent.test',
                       'subject': 'Hello World',
                       'body': 'Test',
                       'thread_id': '',
                       'collection_case': 'collection case1',
                       'reporting_unit': 'reporting case1',
                       'business_name': 'ABusiness',
                       'survey': 'survey'}
    context.response = app.test_client().post(url, data=json.dumps(context.message), headers=headers)


@when('another user tries to send the same message')
def step_impl(context):
    data.update({'msg_id': context.msg_id,
                 'urn_to': 'internal.000000',
                 'urn_from': 'respondent.000000',
                 'subject': 'test',
                 'body': 'test',
                 'thread_id': '2',
                 'collection_case': 'collection case1',
                 'reporting_unit': 'reporting case1',
                 'business_name': 'ABusiness',
                 'survey': 'survey'})

    data['subject'] = 'edited'
    headers['Etag'] = context.etag
    context.response = app.test_client().post(url.format(context.msg_id),
                                             data=json.dumps(data), headers=headers)


@then('is shown a 409 error status')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 409)


# Scenario 13:  Scenario: A Etag is not present within the header
@given('a message is created')
def step_impl(context):
    context.msg = {  'urn_to': 'test',
                     'urn_from': 'test',
                     'subject': 'test',
                     'body': 'Test',
                     'thread_id': '',
                     'collection_case': 'collection case1',
                     'reporting_unit': 'reporting case1',
                     'business_name': 'ABusiness',
                     'survey': 'RSI'}


@when('the message is sent with no Etag')
def step_impl(context):
    if 'ETag' in headers:
        del headers['ETag']

    context.response = app.test_client().post(url, data=json.dumps(context.msg), headers=headers)


# Common Steps: used in multiple scenarios


@when("the message is sent")
def step_impl(context):
    context.response = app.test_client().post(url, data=json.dumps(data), headers=headers)


@then('a msg_id in the response')
def step_impl(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_true(resp['msg_id'] is not None)


@then('a thread_id in the response')
def step_impl(context):
    resp = json.loads(context.response.data)
    nose.tools.assert_true(resp['thread_id'] is not None)


@then("a 400 error status is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@then('a 201 status code is the response')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 201)
