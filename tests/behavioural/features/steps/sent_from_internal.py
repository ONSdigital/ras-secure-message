import nose.tools
from behave import then
from flask import json


@then("sent from internal is '{sent_from_internal}'")
def step_impl_sent_from_internal_is_as_expected(context, sent_from_internal):
    """validate that the ru id in the response is the same as was sent"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['sent_from_internal'], sent_from_internal == 'True')
