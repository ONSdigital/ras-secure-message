import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("new the collection case is set to '{collection_case}'")
@when("new the collection case is set to '{collection_case}'")
def step_impl_the_collection_case_is_set_to(context, collection_case):
    """set the collection case field to a specific value"""
    context.bdd_helper.message_data['collection_case'] = collection_case


@given("new the collection case is too long")
def step_impl_the_msg_collection_case_is_set_too_long(context):
    """set the collection case to a size that is too long"""
    context.bdd_helper.message_data['collection_case'] = "x" * (constants.MAX_COLLECTION_CASE_LEN + 1)


@then("new retrieved message collection case is as was saved")
def step_impl_retrieved_collection_case_is_as_saved(context):
    """validate that thecollection case response matches that in the request"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_case'], context.bdd_helper.last_saved_message_data['collection_case'])


@given("new collection case is set to alternate collection case")
@when("new collection case is set to alternate collection case")
def step_impl_collection_case_set_to_alternate(context):
    """set the collection case to the predefined alternate collection case"""
    context.bdd_helper.use_alternate_collection_case()


@given("new collection case set to default collection case")
@when("new collection case set to default collection case")
def step_impl_collection_case_set_to_default(context):
    """set the collection case to the predefined default collection case"""
    context.bdd_helper.use_default_collection_case()
