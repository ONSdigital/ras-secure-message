import nose.tools
from behave import given, then, when
from flask import json

from secure_message import constants


@given("the from is set to '{msg_from}'")
@when("the from is set to '{msg_from}'")
def step_impl_the_msg_from_is_set_to(context, msg_from):
    """set the msg_from to a specificvalue"""
    context.bdd_helper.message_data['msg_from'] = msg_from


@given("the from is set to empty")
@when("the from is set to empty")
def step_impl_the_msg_from_is_set_to_empty(context):
    """set the from field as empty """
    context.bdd_helper.message_data['msg_from'] = ''


@given("the from is too long")
def step_impl_the_msg_from_is_set_too_long(context):
    """set the from field too long"""
    context.bdd_helper.message_data['msg_from'] = "x" * (constants.MAX_FROM_LEN + 1)


@given("the from is set to respondent")
@when("the from is set to respondent")
def step_impl_the_msg_from_is_set_to_respondent(context):
    """set the from to the respondent as set in the helper """
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.respondent_id)


@given("the from is set to alternative respondent")
@when("the from is set to alternative respondent")
def step_impl_the_msg_from_is_set_to_alternative_respondent(context):
    """set the from to the alternate respondent as set in the helper """
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.alternative_respondent_id)


@given("the from is set to internal non specific user")
@when("the from is set to internal non specific user")
def step_impl_the_msg_from_is_set_to_internal_non_specific_user(context):
    """set the from to the internal user as set in the helper """
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.internal_id_group_user)


@then("retrieved message msg_from is as was saved")
def step_impl_retrieved_msg_from_is_as_saved(context):
    """validate that the responsemessage from field matches that submitted"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_from'], context.bdd_helper.last_saved_message_data['msg_from'])

# V2 Steps below


@given("the from is set to internal group")
@when("the from is set to internal group")
def step_impl_the_msg_from_is_set_to_internal_group_user(context):
    """ set the msg from field in the message data to the internal group  as specified in the helper"""
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.internal_id_group_user)


@given("the from is set to internal specific user")
@when("the from is set to internal specific user")
def step_impl_the_msg_from_is_set_to_internal_specific_user(context):
    """ set the msg from field in the message data to the specific internal user as specified in the helper"""
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.internal_id_specific_user)
