import nose.tools
from behave import given, then, when
from flask import json


@given("the thread_id is set to '{thread_id}'")
@when("the thread_id is set to '{thread_id}'")
def step_impl_the_thread_id_is_set_to(context, thread_id):
    """set the thread id in the message data to a specific value"""
    context.bdd_helper.message_data['thread_id'] = thread_id
    context.thread_id = thread_id


@given("the thread_id is set to empty")
@when("the thread_id is set to empty")
def step_impl_the_thread_id_is_set_to(context):
    """set the thread id in the message data to be empty"""
    context.bdd_helper.message_data['thread_id'] = ""


@given("the thread id is set to the last returned thread id")
@when("the thread id is set to the last returned thread id")
def step_impl_the_thread_id_is_set_to_the_last_returned_thread_id(context):
    """ set the thread id in the message data to be the same as the last retrieved thread id"""
    responses = context.bdd_helper.single_message_responses_data
    thread_id = responses[len(responses)-1]['thread_id']
    context.bdd_helper.message_data['thread_id'] = thread_id
    context.thread_id = thread_id


@given("the thread id is set to that from response '{response_index}'")
@when("the thread id is set to that from response '{response_index}'")
def step_impl_set_thread_id_to_that_in_response_n(context, response_index):
    """set the thread id in message data to that of a specific response """
    thread_id = context.bdd_helper.single_message_responses_data[int(response_index)]['thread_id']
    context.bdd_helper.message_data['thread_id'] = thread_id
    context.thread_id = thread_id


@then("the thread id is equal in all responses")
def step_impl_the_thread_id_is_set_to_the_last_returned_thread_id(context):
    """validate that all single message responses have the same thread id """
    responses = context.bdd_helper.single_message_responses_data
    last_thread_id = responses[len(responses)-1]['thread_id']
    for response in responses:
        nose.tools.assert_equal(response['thread_id'], last_thread_id)


@then("retrieved message thread id is equal to message id")
def step_impl_the_response_message_thread_id_equals_the_message_id(context):
    """validate that the response message id equals the response thread id"""
    response = json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['thread_id'])
    nose.tools.assert_equal(response['thread_id'], response['msg_id'])


@then("retrieved message thread id is not equal to message id")
def step_impl_the_response_message_thread_id_not_equal_to_the_message_id(context):
    """validate that the response thread if does not match the response message id """
    response = json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['thread_id'])
    nose.tools.assert_not_equal(response['thread_id'], response['msg_id'])

