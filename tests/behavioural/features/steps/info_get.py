import nose
from behave import given, then
from flask import json

# Scenario 1: User requests info


@given('the user requests endpoint info')
def step_impl_requests_endpoint_info(context):
    context.response = context.client.get('/info')


@then('the endpoint info is returned')
def step_impl_endpoint_info_is_returned(context):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(response['name'], 'ras-secure-message')
    nose.tools.assert_equal(response['version'], context.app.config['VERSION'])
