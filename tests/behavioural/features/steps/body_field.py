import nose.tools
from behave import given, then, when
from flask import json
from secure_message import constants


@given("the body is set to '{body}'")
@when("the body is set to '{body}'")
def step_impl_the_body_is_set_to(context, body):
    """set the message body to a specific value"""
    context.bdd_helper.message_data['body'] = body


@given("the body is set to include an apostrophe")
@when("the body is set to include an apostrophe")
def step_impl_the_body_is_set_to_include_apostraphe(context):
    """create a body that includes an apostrophe"""
    context.bdd_helper.message_data['body'] = "A body including ' an apostrophe"


@given("the body is set to empty")
@when("the body is set to empty")
def step_impl_the_body_is_set_to_empty(context):
    """empty the message body """
    context.bdd_helper.message_data['body'] = ''


@given("the body is too long")
def step_impl_the_msg_body_is_set_too_long(context):
    """set the body to be longer than that permissable"""
    context.bdd_helper.message_data['body'] = "x" * (constants.MAX_BODY_LEN + 1)


@given("the message body is '{body_length}' characters long")
def step_impl_the_msg_body_is_set_too_long(context, body_length):
    """set the body to be body_length characters long"""
    context.bdd_helper.message_data['body'] = "x" * int(body_length)


@then("retrieved message body is as was saved")
def step_impl_retrieved_body_is_as_saved(context):
    """validate that the received body was the same as was sent"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['body'], context.bdd_helper.last_saved_message_data['body'])


@then("the threads first message body is as was saved")
def step_impl_retrieved_body_is_as_saved(context):
    """validate that the received body of the first message in a thread was the same as was sent"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['messages'][0]['body'], context.bdd_helper.last_saved_message_data['body'])


@then("the message bodies are 100 characters or less")
def step_impl_retrieved_bodies_are_100_characters_or_less(context):
    """validate that the message bodies in a response list are more than 100 characters in length"""
    msg_resp = json.loads(context.response.data)
    for message in msg_resp['messages']:
        nose.tools.assert_less_equal(len(message['body']), 100)
