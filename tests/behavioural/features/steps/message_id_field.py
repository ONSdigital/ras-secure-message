import nose.tools
from behave import given, then, when
from flask import json


@given("the msg_id is set to '{msg_id}'")
@when("the msg_id is set to '{msg_id}'")
def step_impl_the_msg_id_is_set_to(context, msg_id):
    """set the message data messge id to a specific value"""
    context.bdd_helper.message_data['msg_id'] = msg_id
    context.msg_id = msg_id


@then("response includes a msg_id")
def step_impl_response_includes_msg_id(context):
    """validate a response includes a message id of the expected length"""
    returned_data = json.loads(context.response.data)
    nose.tools.assert_true('msg_id' in returned_data)
    nose.tools.assert_true(len(returned_data['msg_id']) == 36)
