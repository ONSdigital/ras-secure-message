import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("new the to is set to '{msg_to}'")
@when("new the to is set to '{msg_to}'")
def step_impl_the_msg_to_is_set_to(context, msg_to):
    """set the msg to field in the message data to a specific value"""
    context.bdd_helper.message_data['msg_to'][0] = msg_to


@given("new the to is set to empty")
@when("new the to is set to empty")
def step_impl_the_msg_to_is_set_to_empty(context):
    """set the message to field in the message data to be empty"""
    context.bdd_helper.message_data['msg_to'][0] = ''


@given("new the to field is too long")
def step_impl_the_msg_to_is_set_too_long(context):
    """set the message to field of the message data to be too long"""
    context.bdd_helper.message_data['msg_to'][0] = "x" * (constants.MAX_TO_LEN+1)


@given("new the to is set to respondent")
@when("new the to is set to respondent")
def step_impl_the_msg_to_is_set_to_respondent(context):
    """ set the msg to field in the message data to the respondent as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.respondent_id)


@given("new the to is set to alternative respondent")
@when("new the to is set to alternative respondent")
def step_impl_the_msg_to_is_set_to_alternative_respondent(context):
    """ set the msg to field in the message data to the alternative respondent as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.alternative_respondent_id)


@given("new the to is set to internal")
@when("new the to is set to internal")
def step_impl_the_msg_to_is_set_to_internal(context):
    """ set the msg to field in the message data to the internal user as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.internal_id)


@given("new the to is set to respondent as a string not array")
@when("new the to is set to respondent as a string not array")
def step_impl_the_msg_to_is_set_to_respondent_as_string_not_array(context):
    """set the message to field to hold a string instead of an array"""
    context.bdd_helper.message_data['msg_to'] = context.bdd_helper.respondent_id


@given("new the to is set to internal user as a string not array")
@when("new the to is set to internal user as a string not array")
def step_impl_the_msg_to_is_set_to_internal_as_string_not_array(context):
    """set the message to to a string not an array"""
    context.bdd_helper.message_data['msg_to'] = context.bdd_helper.internal_id


@then("new retrieved message msg_to is as was saved")
def step_impl_retrieved_msg_to_is_as_saved(context):
    """validate that the message to field in the response is teh same aswas saved"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_to'], context.bdd_helper.last_saved_message_data['msg_to'])