import nose.tools
from behave import given, then, when
from flask import json

from secure_message import constants
from secure_message.constants import NON_SPECIFIC_INTERNAL_USER


@given("the to is set to '{msg_to}'")
@when("the to is set to '{msg_to}'")
def step_impl_the_msg_to_is_set_to(context, msg_to):
    """set the msg to field in the message data to a specific value"""
    context.bdd_helper.message_data["msg_to"][0] = msg_to


@given("the to is set to empty")
@when("the to is set to empty")
def step_impl_the_msg_to_is_set_to_empty(context):
    """set the message to field in the message data to be empty"""
    context.bdd_helper.message_data["msg_to"][0] = ""


@given("the to field is too long")
def step_impl_the_msg_to_is_set_too_long(context):
    """set the message to field of the message data to be too long"""
    context.bdd_helper.message_data["msg_to"][0] = "x" * (constants.MAX_TO_LEN + 1)


@given("the to is set to respondent")
@when("the to is set to respondent")
def step_impl_the_msg_to_is_set_to_respondent(context):
    """set the msg to field in the message data to the respondent as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.respondent_id)


@given("the to is set to alternative respondent")
@when("the to is set to alternative respondent")
def step_impl_the_msg_to_is_set_to_alternative_respondent(context):
    """set the msg to field in the message data to the alternative respondent as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.alternative_respondent_id)


@given("the to is set to a deleted respondent")
@when("the to is set to a deleted respondent")
def step_impl_the_msg_to_is_set_to_deleted_respondent(context):
    """set the msg to field in the message data to the respondent as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.deleted_respondent_id)


@given("the to is set to respondent as a string not array")
@when("the to is set to respondent as a string not array")
def step_impl_the_msg_to_is_set_to_respondent_as_string_not_array(context):
    """set the message to field to hold a string instead of an array"""
    context.bdd_helper.message_data["msg_to"] = context.bdd_helper.respondent_id


@given("the to is set to internal specific user as a string not array")
@when("the to is set to internal specific user as a string not array")
def step_impl_the_msg_to_is_set_to_internal_as_string_not_array(context):
    """set the message to to a string not an array"""
    context.bdd_helper.message_data["msg_to"] = context.bdd_helper.internal_id_specific_user


@then("retrieved message msg_to is as was saved")
def step_impl_retrieved_msg_to_is_as_saved(context):
    """validate that the message to field in the response is the same as was saved"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp["msg_to"], context.bdd_helper.last_saved_message_data["msg_to"])


@given("the to is set to internal group")
@when("the to is set to internal group")
def step_impl_the_msg_to_is_set_to_internal_group_user(context):
    """set the msg to field in the message data to the internal group  as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.internal_id_group_user)


@given("the to is set to internal specific user")
@when("the to is set to internal specific user")
def step_impl_the_msg_to_is_set_to_internal_specific_user(context):
    """set the msg to field in the message data to the specific internal user as specified in the helper"""
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.internal_id_specific_user)


@then("the at_msg_to is set correctly for internal group")
def step_impl_the_at_msg_to_is_set_to_internal_group_user(context):
    msg_resp = json.loads(context.response.data)
    expected = {"id": NON_SPECIFIC_INTERNAL_USER, "firstName": "ONS", "lastName": "User", "emailAddress": ""}
    nose.tools.assert_equal(msg_resp["@msg_to"][0], expected)


@then("the at_msg_to is set correctly for internal group for all messages")
def step_impl_the_at_msg_to_is_set_to_internal_group_user_for_all_messages(context):

    expected = {"id": NON_SPECIFIC_INTERNAL_USER, "firstName": "ONS", "lastName": "User", "emailAddress": ""}
    for msg in context.bdd_helper.messages_responses_data[0]["messages"]:
        nose.tools.assert_equal(msg["@msg_to"][0], expected)
