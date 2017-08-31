import nose.tools
from behave import given, then, when
from flask import json
from app import constants

@given("new the collection_exercise is set to '{collection_exercise}'")
@when("new the collection_exercise is set to '{collection_exercise}'")
def step_impl_the_collection_exercise_is_set_to(context, collection_exercise):
    context.bdd_helper.message_data['collection_exercise'] = collection_exercise



@then("new retrieved message collection exercise is as was saved")
def step_impl_retrieved_collection_exercise_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_exercise'],
                            context.bdd_helper.last_saved_message_data['collection_exercise'])