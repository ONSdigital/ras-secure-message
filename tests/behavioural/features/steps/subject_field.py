import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("new the subject is set to '{subject}'")
@when("new the subject is set to '{subject}'")
def step_impl_the_subject_is_set_to(context, subject):
    """set the subject field in message data to a specific value"""
    context.bdd_helper.message_data['subject'] = subject


@given("new the subject is set to empty")
@when("new the subject is set to empty")
def step_impl_the_subject_is_set_to_empty(context):
    """set the subject field in message data to be empty"""
    context.bdd_helper.message_data['subject'] = ''


@given("new the subject is too long")
def step_impl_the_msg_subject_is_set_too_long(context):
    """set the subject field to be too big"""
    context.bdd_helper.message_data['subject'] = "x" * (constants.MAX_SUBJECT_LEN + 1)


@then("new retrieved message subject is as was saved")
def step_impl_retrieved_subject_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    """validate that the retrieved message subject matches that sent"""
    nose.tools.assert_equal(msg_resp['subject'], context.bdd_helper.last_saved_message_data['subject'])