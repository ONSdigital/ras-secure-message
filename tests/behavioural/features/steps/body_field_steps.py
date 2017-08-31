import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("new the body is set to '{body}'")
@when("new the body is set to '{body}'")
def step_impl_the_body_is_set_to(context, body):
    context.bdd_helper.message_data['body'] = body


@given("new the body is set to include an apostrophe")
@when("new the body is set to include an apostrophe")
def step_impl_the_body_is_set_to(context):
    context.bdd_helper.message_data['body'] = "A body including ' an apostrophe"


@given("new the body is set to empty")
@when("new the body is set to empty")
def step_impl_the_body_is_set_to_empty(context):
    context.bdd_helper.message_data['body'] = ''


@given("new the body is too long")
def step_impl_the_msg_body_is_set_too_long(context):
    context.bdd_helper.message_data['body'] = "x" * (constants.MAX_BODY_LEN + 1)


@then("new retrieved message body is as was saved")
def step_impl_retrieved_body_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['body'], context.bdd_helper.last_saved_message_data['body'])