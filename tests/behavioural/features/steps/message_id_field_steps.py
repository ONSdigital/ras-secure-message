import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("new the msg_id is set to '{msg_id}'")
@when("new the msg_id is set to '{msg_id}'")
def step_impl_the_msg_id_is_set_to(context, msg_id):
    context.bdd_helper.message_data['msg_id'] = msg_id
    context.msg_id = msg_id


@then("new retrieved message msg_to is as was saved")
def step_impl_retrieved_msg_to_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_to'], context.bdd_helper.last_saved_message_data['msg_to'])
