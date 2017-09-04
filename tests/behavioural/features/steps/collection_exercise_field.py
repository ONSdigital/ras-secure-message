import nose.tools
from behave import given, then, when
from flask import json
from app import constants


@given("the collection_exercise is set to '{collection_exercise}'")
@when("the collection_exercise is set to '{collection_exercise}'")
def step_impl_the_collection_exercise_is_set_to(context, collection_exercise):
    """set the collection exercise to a specific value"""
    context.bdd_helper.message_data['collection_exercise'] = collection_exercise


@then("retrieved message collection exercise is as was saved")
def step_impl_retrieved_collection_exercise_is_as_saved(context):
    """validate that the collection exercise is teh same as was saved"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_exercise'],
                            context.bdd_helper.last_saved_message_data['collection_exercise'])


@given("collection exercise is set to alternate collection exercise")
@when("collection exercise is set to alternate collection exercise")
def step_impl_collection_exercise_set_to_alternate(context):
    """set the collection exercise to the previoulsy defined alternate value"""
    context.bdd_helper.use_alternate_collection_exercise()


@given("collection exercise set to default collection exercise")
@when("collection exercise set to default collection exercise")
def step_impl_collection_exercise_set_to_default(context):
    """set the collection exercise to the previously defined default value"""
    context.bdd_helper.use_default_collection_exercise()

@given("the collection exercise is too long")
def step_impl_the_msg_collection_exercise_is_set_too_long(context):
    """set the collection exercise to a value that is too long"""
    context.bdd_helper.message_data['collection_exercise'] = "x" * (constants.MAX_COLLECTION_EXERCISE_LEN + 1)