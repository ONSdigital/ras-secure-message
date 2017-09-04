import nose.tools
from behave import given, then, when
from flask import json


@then("the response message has the label '{label}'")
def step_impl_the_response_message_should_have_named_label(context, label):
    """validate that theresponse has a specific label"""
    response = json.loads(context.response.data)
    nose.tools.assert_true(label in response['labels'])


@then("all response messages have the label '{label}'")
def step_impl_the_response_messages_should_all_have_named_label(context, label):
    """validate all messages in a response have as pecific label"""
    for response in context.bdd_helper.messages_responses_data[0]['messages']:
        nose.tools.assert_true(label in response['labels'])


@then("the response message does not have the label '{label}'")
def step_impl_the_response_message_should_not_have_named_label(context, label):
    """validate that the response does not have a specific label"""
    response = json.loads(context.response.data)
    nose.tools.assert_false(label in response['labels'])


@then("the response message should a label count of '{label_count}'")
def step_impl_the_response_message_should_have_named_label(context, label_count):
    """validate that the label count in the response matches a specific number"""
    response = json.loads(context.response.data)
    nose.tools.assert_equal(len(response['labels']), int(label_count))


@given("a label of '{label}' is to be added")
@when("a label of '{label}' is to be added")
def step_impl_a_named_label_is_to_be_added(context, label):
    """prepare the message data so as to add a label of a specific name"""
    context.bdd_helper.message_data = {"action": "add", "label": label}


@given("a label of '{label}' is to be removed")
@when("a label of '{label}' is to be removed")
def step_impl_a_named_label_is_to_be_removed(context, label):
    """remove a specific label from the message data to be sent"""
    context.bdd_helper.message_data = {"action": "remove", "label": label}


@given("a label of '{label}' has unknown action")
@when("a label of '{label}' has unknown action")
def step_impl_a_named_label_is_to_be_removed(context, label):
    """specify a label action that is not 'add' or 'remove' """
    context.bdd_helper.message_data = {"action": "some_unknown_action", "label": label}


@then("'{message_count}' messages have a '{label}' label")
def step_impl_n_messages_have_specific_label(context, message_count, label):
    """validate that a specific number of messages in a reply have a specific label"""
    label_count = 0
    for response in context.bdd_helper.messages_responses_data[0]['messages']:
        if label in response['labels']:
            label_count += 1
    nose.tools.assert_equal(int(message_count), label_count)
