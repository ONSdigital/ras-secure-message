import nose
from behave import given, then
from flask import json
from app.application import app


# Scenario 1: User requests info


@given('the user requests endpoint info')
def step_impl_requests_endpoint_info(context):
    context.response = app.test_client().get('/info')


@then('the endpoint info is returned')
def step_impl_endpoint_info_is_returned(context):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(response['name'], 'secure_message')
    nose.tools.assert_equal(response['version'], '0.0.1')
    nose.tools.assert_equal(response['origin'], 'https://github.com/ONSdigital/ras-secure-message.git')
    nose.tools.assert_equal(response['commit'], 'not specified')
    nose.tools.assert_equal(response['branch'], 'not specified')
    nose.tools.assert_equal(response['built'], '01-01-1900 00:00:00.000')
