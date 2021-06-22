import nose.tools
from behave import given, then, when
from flask import json


@given("the survey is set to '{survey_id}'")
@when("the survey is set to '{survey_id}'")
def step_impl_the_survey_is_set_to(context, survey_id):
    """the survey in message data is set to s pecific value"""
    context.bdd_helper.message_data['survey_id'] = survey_id


@given("the survey is set to empty")
@when("the survey is set to empty")
def step_impl_the_survey_is_set_to_empty(context):
    """the survey in message data is set to be empty"""
    context.bdd_helper.message_data['survey_id'] = ''


@then("retrieved message survey is as was saved")
def step_impl_retrieved_survey_is_as_saved(context):
    """validate that the retrieved survey matches that which was last sent"""
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['survey_id'], context.bdd_helper.last_saved_message_data['survey_id'])


@given("survey is set to alternate survey")
@when("survey is set to alternate survey")
def step_impl_survey_set_to_alternate(context):
    """set the message data survey field to be that of the alternativedefault survey as in the helper"""
    context.bdd_helper.use_alternate_survey()


@given("survey set to default survey")
@when("survey set to default survey")
def step_impl_survey_set_to_default(context):
    """set the message data survey field to be that of the default survey as in the helper"""
    context.bdd_helper.use_default_survey()


@when("the survey_id of the message is changed to '{survey_id}'")
def step_impl_the_response_message_thread_is_closed(context, survey_id):
    """close the conversation of the last saved message"""
    msg_id = context.bdd_helper.single_message_responses_data[0]['msg_id']
    url = context.bdd_helper.message_patch_url.format(msg_id)
    context.response = context.client.patch(url, data=json.dumps({"survey_id": survey_id}),
                                            headers=context.bdd_helper.headers)


@when("the survey_id of the message is changed to an empty string")
def step_impl_the_response_message_thread_is_closed(context):  # noqa: F811
    """close the conversation of the last saved message"""
    msg_id = context.bdd_helper.single_message_responses_data[0]['msg_id']
    url = context.bdd_helper.message_patch_url.format(msg_id)
    context.response = context.client.patch(url, data=json.dumps({"survey_id": ""}),
                                            headers=context.bdd_helper.headers)
