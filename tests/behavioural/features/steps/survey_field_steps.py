import nose.tools
from behave import given, then, when
from flask import json



@given("new the survey is set to '{survey}'")
@when("new the survey is set to '{survey}'")
def step_impl_the_survey_is_set_to(context, survey):
    context.bdd_helper.message_data['survey'] = survey


@given("new the survey is set to empty")
@when("new the survey is set to empty")
def step_impl_the_survey_is_set_to_empty(context):
    context.bdd_helper.message_data['survey'] = ''


@then("new retrieved message survey is as was saved")
def step_impl_retrieved_survey_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['survey'], context.bdd_helper.last_saved_message_data['survey'])