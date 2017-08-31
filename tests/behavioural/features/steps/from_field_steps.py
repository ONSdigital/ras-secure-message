import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("new the from is set to '{msg_from}'")
@when("new the from is set to '{msg_from}'")
def step_impl_the_msg_from_is_set_to(context, msg_from):
    context.bdd_helper.message_data['msg_from'] = msg_from


@given("new the from is set to empty")
@when("new the from is set to empty")
def step_impl_the_msg_from_is_set_to_empty(context):
    context.bdd_helper.message_data['msg_from'] = ''


@given("new the from is too long")
def step_impl_the_msg_from_is_set_too_long(context):
    context.bdd_helper.message_data['msg_from'] = "x" * (constants.MAX_FROM_LEN + 1)


@given("new the from is set to respondent")
@when("new the from is set to respondent")
def step_impl_the_msg_from_is_set_to_respondent(context):
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.respondent_id)


@given("new the from is set to alternative respondent")
@when("new the from is set to alternative respondent")
def step_impl_the_msg_from_is_set_to_alternative_respondent(context):
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.alternative_respondent_id)


@given("new the from is set to internal")
@when("new the from is set to internal")
def step_impl_the_msg_from_is_set_to_internal(context):
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.internal_id)


@then("new retrieved message msg_from is as was saved")
def step_impl_retrieved_msg_from_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_from'], context.bdd_helper.last_saved_message_data['msg_from'])