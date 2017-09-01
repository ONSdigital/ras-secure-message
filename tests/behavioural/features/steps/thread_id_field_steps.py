import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("new the thread_id is set to '{thread_id}'")
@when("new the thread_id is set to '{thread_id}'")
def step_impl_the_thread_id_is_set_to(context, thread_id):
    context.bdd_helper.message_data['thread_id'] = thread_id


@given("new the thread id is set to the last returned thread id")
@when("new the thread id is set to the last returned thread id")
def step_impl_the_thread_id_is_set_to_the_last_returned_thread_id(context):
    responses = context.bdd_helper.single_message_responses_data
    thread_id = responses[len(responses)-1]['thread_id']
    context.bdd_helper.message_data['thread_id'] = thread_id


@then("new the thread id is equal in all responses")
def step_impl_the_thread_id_is_set_to_the_last_returned_thread_id(context):
    responses = context.bdd_helper.single_message_responses_data
    last_thread_id = responses[len(responses)-1]['thread_id']
    for response in responses:
        nose.tools.assert_equals(response['thread_id'], last_thread_id)


@then("new retrieved message thread id is equal to message id")
def step_impl_the_response_message_thread_id_equals_the_message_id(context):
    response = json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['thread_id'])
    nose.tools.assert_equal(response['thread_id'], response['msg_id'])


@then("new retrieved message thread id is not equal to message id")
def step_impl_the_response_message_thread_id_not_equal_to_the_message_id(context):
    response = json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['thread_id'])
    nose.tools.assert_not_equal(response['thread_id'], response['msg_id'])

