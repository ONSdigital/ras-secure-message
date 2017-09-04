from app.application import app
from behave import given, when
from flask import json
import copy


# These steps genrate http requests and responses

@given("new the message is sent")
@when("new the message is sent")
def step_impl_the_message_is_sent(context):
    """sends the current message data to the message send endpoint"""
    context.bdd_helper.sent_messages.extend([copy.deepcopy(context.bdd_helper.message_data)])
    context.response = app.test_client().post(context.bdd_helper.message_post_url,
                                              data=json.dumps(context.bdd_helper.message_data),
                                              headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("new the draft is sent as a message")
@when("new the draft is sent as a message")
def step_impl_the_draft_is_sent_as_message(context):
    """sends a message that was a draft as a message """
    context.bdd_helper.message_data['msg_id'] = context.msg_id
    step_impl_the_message_is_sent(context)
    context.bdd_helper.message_data['msg_id'] = ""


@given("new '{message_count}' messages are sent")
@when("new '{message_count}' messages are sent")
def step_impl_the_n_messages_are_sent(context, message_count):
    """sends a defined number of messages"""
    for i in range(0, int(message_count)):
        step_impl_the_message_is_sent(context)


@given("new the message is saved as draft")
@when("new the message is saved as draft")
def step_impl_the_message_is_saved_as_draft(context):
    """saves the current message data as a draft via  draft post """
    context.bdd_helper.sent_messages.extend([copy.deepcopy(context.bdd_helper.message_data)])
    context.response = app.test_client().post(context.bdd_helper.draft_post_url,
                                              data=json.dumps(context.bdd_helper.message_data),
                                              headers=context.bdd_helper.headers)
    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("new '{draft_count}' drafts are sent")
@when("new '{draft_count}' drafts are sent")
def step_impl_the_n_drafts_are_sent(context, draft_count):
    """saves a specific number of drafts """
    for i in range(0, int(draft_count)):
        step_impl_the_message_is_saved_as_draft(context)


@given("new the message is read")
@when("new the message is read")
def step_impl_the_previously_saved_message_is_retrieved(context):
    """reads message with the id saved in the context via the message get endpoint"""
    url = context.bdd_helper.message_get_url.format(context.msg_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@when("new the message with id '{msg_id}' is retrieved")
@given("new the message with id '{msg_id}' is retrieved")
def step_impl_the_specific_message_id_is_retrieved(context, msg_id):
    """retrieve a message with a specific id (e.g one that does not exist)"""
    url = context.bdd_helper.message_get_url.format(msg_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@when("new the message labels are modified")
@given("new the message labels are modified")
def step_impl_the_message_labels_are_modified(context):
    """update the labels on the messages identified by the context.msg_id"""
    step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id(context, context.msg_id)


@when("new the message labels are modified on msg id '{msg_id}'")
@given("new the message labels are modified on msg id '{msg_id}'")
def step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id(context, msg_id):
    """modify the labels on a specified message id"""
    url = context.bdd_helper.message_put_url.format(msg_id)

    context.response = app.test_client().put(url, data=json.dumps(context.bdd_helper.message_data),
                                             headers=context.bdd_helper.headers)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("new the previously returned draft is modified")
@when("new the previously returned draft is modified")
def step_impl_update_draft_message(context):
    """modify a previosly saved draft"""
    _update_draft_message_with_specific_data_msg_id(context, context.msg_id)


@given("new the previously returned draft is modified where data message id does not match url")
@when("new the previously returned draft is modified where data message id does not match url")
def step_impl_update_draft_message_msg_ids_mismatched(context):
    """update a draft using data in the message body that does not match the url"""
    _update_draft_message_with_specific_data_msg_id(context, '12345')


def _update_draft_message_with_specific_data_msg_id(context, msg_id):
    """helper function to update draft information on a specific message id"""
    url = context.bdd_helper.draft_put_url.format(context.msg_id)
    sent_data = context.bdd_helper.message_data
    sent_data['msg_id'] = msg_id           #usually context.msg_id
    context.bdd_helper.sent_messages.extend([sent_data])
    context.response = app.test_client().put(url,
                                             data=json.dumps(sent_data),
                                             headers=context.bdd_helper.headers)
    if context.response.status_code == 200:
        context.bdd_helper.store_last_single_message_response_data(context.response)


@given("new the draft is read")
@when("new the draft is read")
def step_impl_the_previously_saved_draft_is_retrieved(context):
    """read a draft"""
    url = context.bdd_helper.draft_get_url.format(context.msg_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("new messages are read")
@when("new messages are read")
def step_impl_messages_are_read(context):
    """get a message list"""
    url = context.bdd_helper.messages_get_url
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    context.bdd_helper.store_messages_response_data(response_data)


@given("new messages are read with '{limit}' per page requesting page '{page}'")
@when("new messages are read with '{limit}' per page requesting page '{page}'")
def step_impl_messages_read_with_specific_limit_per_page_requesting_specific_page(context, limit, page):
    """get a message list with limit and page parameters"""
    param = "?limit={}&page={}".format(int(limit), int(page))
    url = context.bdd_helper.messages_get_url+param
    _step_impl_get_messages_with_filter(context, url)


@given("new messages are read using current '{param_name}'")
@when("new messages are read using current '{param_name}'")
def step_impl_messages_are_read_with_filter_of_current_param_value(context, param_name):
    """restrict messages in get messages to those with a named parameter that matches the value in message data"""
    param_value = context.bdd_helper.message_data[param_name]
    param_name = 'cc' if param_name == 'collection_case' else param_name
    param_name = 'ce' if param_name == 'collection_exercise' else param_name
    param = "?{}={}".format(param_name, param_value)
    url = context.bdd_helper.messages_get_url+param
    _step_impl_get_messages_with_filter(context, url)


@given("new messages with a label of  '{label_name}' are read")
@when("new messages with a label of  '{label_name}' are read")
def step_impl_messages_are_read_with_filter_of_current_param_value(context, label_name):
    """filter get messages to only return messages matching a specified label"""
    param = "?label={}".format(label_name)
    url = context.bdd_helper.messages_get_url+param
    _step_impl_get_messages_with_filter(context, url)


def _step_impl_get_messages_with_filter(context, url):
    """helper function to get messages"""
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@given("new drafts are read")
@when("new drafts are read")
def step_impl_drafts_are_read(context):
    """read draft messages"""
    url = context.bdd_helper.drafts_get_url
    _step_impl_drafts_are_read(context, url)


@given("new drafts are read with '{limit}' per page requesting page '{page}'")
@when("new drafts are read with '{limit}' per page requesting page '{page}'")
def step_impl_drafts_read_with_specific_limit_per_page_requesting_specific_page(context, limit, page):
    """draft messages are read with a specific limit per page and specific page number"""
    param = "?limit={}&page={}".format(int(limit), int(page))
    url = context.bdd_helper.messages_get_url+param
    _step_impl_drafts_are_read(context, url)


def _step_impl_drafts_are_read(context, url):
    """ common function to read drafts"""
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    context.bdd_helper.store_messages_response_data(response_data)


@given("new drafts are read using current '{param_name}'")
@when("new drafts are read using current '{param_name}'")
def step_impl_drafts_are_read_with_filter_of_current_param_value(context, param_name):
    """read drafts, limiting them to messages that have a parameter with the same value as that in message data"""
    param_value = context.bdd_helper.message_data[param_name]
    param_name = 'cc' if param_name == 'collection_case' else param_name
    param_name = 'ce' if param_name == 'collection_exercise' else param_name
    param = "?{}={}".format(param_name, param_value)
    url = context.bdd_helper.messages_get_url+param
    _step_impl_get_drafts_with_filter(context, url)


def _step_impl_get_drafts_with_filter(context, url):
    """common function to get grafts"""
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@given("new drafts with a label of  '{label_name}' are read")
@when("new drafts with a label of  '{label_name}' are read")
def step_impl_drafts_are_read_with_filter_of_current_param_value(context, label_name):
    """reads drafts with a specified label"""
    param = "?label={}".format(label_name)
    url = context.bdd_helper.messages_get_url + param
    _step_impl_get_drafts_with_filter(context, url)


@given("new the thread is read")
@when("new the thread is read")
def step_impl_the_thread_is_read(context):
    """read a specific thread based on context thread id"""
    url = context.bdd_helper.thread_get_url.format(context.thread_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)

    context.bdd_helper.store_messages_response_data(context.response.data)


def _try_persist_msg_and_thread_id_to_context(context, returned_data):
    """common function used to extract msg_id and thread_id from returned messages"""
    if 'msg_id' in returned_data:
        context.msg_id = returned_data['msg_id']
    else:
        context.msg_id = "NOT RETURNED"

    if 'thread_id' in returned_data:
        context.thread_id = returned_data['thread_id']
    else:
        context.thread_id = "NOT RETURNED"


@given("new the threads are read")
@when("new the threads are read")
def step_impl_the_threads_are_read(context):
    """reads a list of threads"""
    url = context.bdd_helper.threads_get_url.format(context.thread_id)
    context.response = app.test_client().get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)




