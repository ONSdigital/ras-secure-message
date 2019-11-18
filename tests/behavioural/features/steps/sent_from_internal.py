import nose.tools
from behave import then
from flask import json


@then("sent from internal is '{from_internal}'")
def step_impl_from_internal_is_as_expected(context, from_internal):
    """validate that the business_id in the response is the same as was sent"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['from_internal'], from_internal == 'True')


@then("'{from_internal_count}' messages are returned with sent from internal")
def step_impl_from_internal_true_count(context, from_internal_count):
    """validate that the business_id in the response is the same as was sent"""
    response_count = 0

    for response in context.bdd_helper.messages_responses_data[0]['messages']:
        if response['from_internal']:
            response_count += 1
    nose.tools.assert_equal(response_count, int(from_internal_count))
