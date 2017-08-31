import nose.tools
from app.application import app
from behave import given, then, when
from flask import json


@given("new the message is sent")
@when("new the message is sent")
def step_impl_the_message_is_sent(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = app.test_client().post(context.bdd_helper.message_post_url,
                                              data=json.dumps(context.bdd_helper.message_data),
                                              headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    if 'msg_id' in returned_data:
        context.msg_id = returned_data['msg_id']
    else:
        context.msg_id = "NOT RETURNED"

    if 'thread_id' in returned_data:
        context.thread_id = returned_data['thread_id']
    else:
        context.thread_id = "NOT RETURNED"
    context.bdd_helper.store_response_data(context.response)


@given("new '{message_count}' messages are sent")
@when("new '{message_count}' messages are sent")
def step_impl_the_n_messages_are_sent(context, message_count):
    for i in range(1, message_count):
        step_impl_the_message_is_sent(context)


@given("new the message is saved as draft")
@when("new the message is saved as draft")
def step_impl_the_message_is_saved_as_draft(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = app.test_client().post(context.bdd_helper.draft_post_url,
                                              data=json.dumps(context.bdd_helper.message_data),
                                              headers=context.bdd_helper.headers)
    returned_data = json.loads(context.response.data)
    if 'msg_id' in returned_data:
        context.msg_id = returned_data['msg_id']
    else:
        context.msg_id = "NOT RETURNED"
    if 'thread_id' in returned_data:
        context.thread_id = returned_data['thread_id']
    else:
        context.thread_id = "NOT RETURNED"
    context.bdd_helper.store_response_data(context.response)


@given("new the message is read")
@when("new the message is read")
def step_impl_the_previously_saved_message_is_retrieved(context):
    url = context.bdd_helper.message_get_url.format(context.msg_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    returned_data = json.loads(context.response.data)
    if 'msg_id' in returned_data:
        context.msg_id = returned_data['msg_id']
    else:
        context.msg_id = "NOT RETURNED"
    if 'thread_id' in returned_data:
        context.thread_id = returned_data['thread_id']
    else:
        context.thread_id = "NOT RETURNED"
    context.bdd_helper.store_response_data(context.response)


@when("new the message with id '{msg_id}' is retrieved")
@given("new the message with id '{msg_id}' is retrieved")
def step_impl_the_specific_message_id_is_retrieved(context, msg_id):
    url = context.bdd_helper.message_get_url.format(msg_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_response_data(context.response)


@when("new the message labels are modified")
@given("new the message labels are modified")
def step_impl_the_specific_message_id_is_retrieved(context):
    step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id(context, context.msg_id)


@when("new the message labels are modified on msg id '{msg_id}'")
@given("new the message labels are modified on msg id '{msg_id}'")
def step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id(context, msg_id):
    url = context.bdd_helper.message_put_url.format(msg_id)

    context.response = app.test_client().put(url, data=json.dumps(context.bdd_helper.message_data),
                                             headers=context.bdd_helper.headers)
    context.bdd_helper.store_response_data(context.response)


@given("new the previously returned draft is modified")
@when("new the previously returned draft is modified")
def step_impl_update_draft_message(context):
    _update_draft_message_with_specific_data_msg_id(context, context.msg_id)


@given("new the previously returned draft is modified where data message id does not match url")
@when("new the previously returned draft is modified where data message id does not match url")
def step_impl_update_draft_message_msg_ids_mismatched(context):
    _update_draft_message_with_specific_data_msg_id(context, '12345')


def _update_draft_message_with_specific_data_msg_id(context, msg_id):
    url = context.bdd_helper.draft_put_url.format(context.msg_id)
    sent_data = context.bdd_helper.message_data
    sent_data['msg_id'] = msg_id           #usually context.msg_id
    context.bdd_helper.sent_messages.extend([sent_data])
    context.response = app.test_client().put(url,
                                             data=json.dumps(sent_data),
                                             headers=context.bdd_helper.headers)
    if context.response.status_code == 200:
        context.bdd_helper.store_response_data(context.response)


@given("new the draft is read")
@when("new the draft is read")
def step_impl_the_previously_saved_draft_is_retrieved(context):
    url = context.bdd_helper.draft_get_url.format(context.msg_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    if 'msg_id' in returned_data:
        context.msg_id = returned_data['msg_id']
    else:
        context.msg_id = "NOT RETURNED"

    if 'thread_id' in returned_data:
        context.thread_id = returned_data['thread_id']
    else:
        context.thread_id = "NOT RETURNED"
    context.bdd_helper.store_response_data(context.response)

@then("new response includes a msg_id")
def step_impl_response_includes_msg_id(context ):
    returned_data = json.loads(context.response.data)
    nose.tools.assert_true('msg_id' in returned_data)
    nose.tools.assert_true(len(returned_data['msg_id']) == 36)
