import nose.tools
from behave import given, then, when
from flask import json


@given("the ru is set to '{ru}'")
@when("the ru is set to '{ru}'")
def step_impl_the_ru_is_set_to(context, ru):
    """set the message data ru to a specific value"""
    context.bdd_helper.message_data['ru'] = ru


@then("retrieved message ru is as was saved")
def step_impl_retrieved_ru_id_is_as_saved(context):
    """validate that the ru id in the response is the same as was sent"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['ru_id'], context.bdd_helper.last_saved_message_data['ru_id'])


@given("ru set to alternate ru")
@when("ru set to alternate ru")
def step_impl_ru_set_to_alternate(context):
    """set the ru id in the message data to that of the default alternative value as specified in the helper"""
    context.bdd_helper.use_alternate_ru()


@given("ru set to default ru")
@when("ru set to default ru")
def step_impl_ru_set_to_default(context):
    """set the ru id in the message data to that of the default  value as specified in the helper"""
    context.bdd_helper.use_default_ru()
