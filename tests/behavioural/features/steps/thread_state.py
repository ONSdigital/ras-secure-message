from behave import given, when
from flask import json


@when("the last returned thread is closed")
@given("the last returned thread is closed")
def step_impl_the_response_message_thread_is_closed(context):
    """close the conversation of the last saved message"""
    thread_id = context.bdd_helper.single_message_responses_data[0]['thread_id']
    url = context.bdd_helper.thread_get_url.format(thread_id)
    context.response = context.client.patch(url, data=json.dumps({"is_closed": True}),
                                            headers=context.bdd_helper.headers)


@when("the category of the thread is changed to '{category}'")
def step_impl_the_response_message_thread_is_closed(context, category):  # noqa: F811
    """close the conversation of the last saved message"""
    thread_id = context.bdd_helper.single_message_responses_data[0]['thread_id']
    url = context.bdd_helper.thread_get_url.format(thread_id)
    context.response = context.client.patch(url, data=json.dumps({"category": category}),
                                            headers=context.bdd_helper.headers)
