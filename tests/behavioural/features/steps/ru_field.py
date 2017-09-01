import nose.tools
from behave import given, then, when
from flask import json


@given("new the ru is set to '{ru}'")
@when("new the ru is set to '{ru}'")
def step_impl_the_ru_is_set_to(context, ru):
    context.bdd_helper.message_data['ru'] = ru


@then("new retrieved message ru is as was saved")
def step_impl_retrieved_ru_id_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['ru_id'], context.bdd_helper.last_saved_message_data['ru_id'])


@given("new ru set to alternate ru")
@when("new ru set to alternate ru")
def step_impl_ru_set_to_alternate(context):
    context.bdd_helper.use_alternate_ru()


@given("new ru set to default ru")
@when("new ru set to default ru")
def step_impl_ru_set_to_default(context):
    context.bdd_helper.use_default_ru()