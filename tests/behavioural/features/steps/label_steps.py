import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@then("new the response message has the label '{label}'")
def step_impl_the_response_message_should_have_named_label(context, label):
    response = json.loads(context.response.data)
    nose.tools.assert_true(label in response['labels'])


@then("new all response messages have the label '{label}'")
def step_impl_the_response_messages_should_all_have_named_label(context, label):
    for response in context.bdd_helper.messages_responses_data[0]['messages']:
        nose.tools.assert_true(label in response['labels'])


@then("new the response message does not have the label '{label}'")
def step_impl_the_response_message_should_not_have_named_label(context, label):
    response = json.loads(context.response.data)
    nose.tools.assert_false(label in response['labels'])


@then("new the response message should a label count of '{label_count}'")
def step_impl_the_response_message_should_have_named_label(context, label_count):
    response = json.loads(context.response.data)
    nose.tools.assert_equal(len(response['labels']), int(label_count))


@given("new a label of '{label}' is to be added")
@when("new a label of '{label}' is to be added")
def step_impl_a_named_label_is_to_be_added(context, label):
    context.bdd_helper.message_data={"action": "add", "label": label}


@given("new a label of '{label}' is to be removed")
@when("new a label of '{label}' is to be removed")
def step_impl_a_named_label_is_to_be_removed(context, label):
    context.bdd_helper.message_data={"action": "remove", "label": label}


@given("new a label of '{label}' has unknown action")
@when("new a label of '{label}' has unknown action")
def step_impl_a_named_label_is_to_be_removed(context, label):
    context.bdd_helper.message_data={"action": "some_unknown_action", "label": label}


@then("new '{message_count}' messages have a '{label}' label")
def step_impl_n_messages_have_specific_label(context, message_count, label):
    label_count=0
    for response in context.bdd_helper.messages_responses_data[0]['messages']:
        if label in response['labels']:
            label_count += 1
    nose.tools.assert_equal(int(message_count), label_count)
