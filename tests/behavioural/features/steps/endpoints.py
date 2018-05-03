import copy

from behave import given, when
from flask import json


# These steps generate http requests and responses

@given("the message is sent")
@when("the message is sent")
def step_impl_the_message_is_sent(context):
    """sends the current message data to the message send endpoint"""
    context.bdd_helper.sent_messages.extend([copy.deepcopy(context.bdd_helper.message_data)])
    context.response = context.client.post(context.bdd_helper.message_post_url,
                                           data=json.dumps(context.bdd_helper.message_data),
                                           headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("'{message_count}' messages are sent")
@when("'{message_count}' messages are sent")
def step_impl_the_n_messages_are_sent(context, message_count):
    """sends a defined number of messages"""
    for i in range(0, int(message_count)):
        step_impl_the_message_is_sent(context)


@given("the message is read")
@when("the message is read")
def step_impl_the_previously_saved_message_is_retrieved(context):
    """reads message with the id saved in the context via the message get endpoint"""
    url = context.bdd_helper.message_get_url.format(context.msg_id)
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@when("the message with id '{msg_id}' is retrieved")
@given("the message with id '{msg_id}' is retrieved")
def step_impl_the_specific_message_id_is_retrieved(context, msg_id):
    """retrieve a message with a specific id (e.g one that does not exist)"""
    url = context.bdd_helper.message_get_url.format(msg_id)
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@when("the message labels are modified")
@given("the message labels are modified")
def step_impl_the_message_labels_are_modified(context):
    """update the labels on the messages identified by the context.msg_id"""
    step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id(context, context.msg_id)


@when("the message labels are modified on msg id '{msg_id}'")
@given("the message labels are modified on msg id '{msg_id}'")
def step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id(context, msg_id):
    """modify the labels on a specified message id"""
    url = context.bdd_helper.message_put_url.format(msg_id)

    context.response = context.client.put(url, data=json.dumps(context.bdd_helper.message_data),
                                          headers=context.bdd_helper.headers)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("messages are read")
@when("messages are read")
def step_impl_messages_are_read(context):
    """get a message list"""
    url = context.bdd_helper.messages_get_url
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    context.bdd_helper.store_messages_response_data(response_data)


@given("messages are read with '{limit}' per page requesting page '{page}'")
@when("messages are read with '{limit}' per page requesting page '{page}'")
def step_impl_messages_read_with_specific_limit_per_page_requesting_specific_page(context, limit, page):
    """get a message list with limit and page parameters"""
    param = f"?limit={int(limit)}&page={int(page)}"
    url = context.bdd_helper.messages_get_url + param
    _step_impl_get_messages_with_filter(context, url)


@given("messages are read using current '{param_name}'")
@when("messages are read using current '{param_name}'")
def step_impl_messages_are_read_with_filter_of_current_param_value(context, param_name):
    """restrict messages in get messages to those with a named parameter that matches the value in message data"""
    param_value = context.bdd_helper.message_data[param_name]
    param_name = 'cc' if param_name == 'collection_case' else param_name
    param_name = 'ce' if param_name == 'collection_exercise' else param_name
    param = f"?{param_name}={param_value}"
    url = context.bdd_helper.messages_get_url + param
    _step_impl_get_messages_with_filter(context, url)


@given("messages with a label of  '{label_name}' are read")
@when("messages with a label of  '{label_name}' are read")
def step_impl_messages_are_read_with_specific_label(context, label_name):
    """filter get messages to only return messages matching a specified label"""
    param = f"?label={label_name}"
    url = context.bdd_helper.messages_get_url + param
    _step_impl_get_messages_with_filter(context, url)


def _step_impl_get_messages_with_filter(context, url):
    """helper function to get messages"""
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@given("the thread is read")
@when("the thread is read")
def step_impl_the_thread_is_read(context):
    """read a specific thread based on context thread id"""
    url = context.bdd_helper.thread_get_url.format(context.thread_id)
    context.response = context.client.get(url, headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)

    context.bdd_helper.store_messages_response_data(context.response.data)


@given("the last '{message_count}' messages of thread are read")
@when("the last '{message_count}' messages of thread are read")
def step_impl_the_last_n_messages_of_thread_are_read(context):
    """read a specific thread based on context thread id"""
    url = context.bdd_helper.thread_get_url.format(context.thread_id)
    context.response = context.client.get(url, headers=context.bdd_helper.headers)

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


@given("the threads are read")
@when("the threads are read")
def step_impl_the_threads_are_read(context):
    """reads a list of threads"""
    url = context.bdd_helper.threads_get_url.format(context.thread_id)
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads in survey '{survey}' are read")
@given("the threads in survey '{survey}' are read")
def step_impl_the_threads_in_specific_survey_are_returned(context, survey):
    url = context.bdd_helper.threads_get_url + f"?survey={survey}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads in are read with filters for both default and alternate surveys")
def step_impl_the_threads_in_default_and_alternate_are_returned(context):
    url = context.bdd_helper.threads_get_url + f"?survey={context.bdd_helper.default_survey}" \
                                               f"&survey={context.bdd_helper.alternate_survey}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads with ru '{ru_id}' are read")
@given("the threads with ru '{ru_id}' are read")
def step_impl_the_threads_in_specific_ru_id_are_returned(context, ru_id):
    url = context.bdd_helper.threads_get_url + f"?ru_id={ru_id}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads with collection case '{cc}' are read")
@given("the threads with collection case '{cc}' are read")
def step_impl_the_threads_in_specific_collection_case_id_are_returned(context, cc):
    url = context.bdd_helper.threads_get_url + f"?cc={cc}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads with collection exercise '{ce}' are read")
@given("the threads with collection exercise '{ce}' are read")
def step_impl_the_threads_in_specific_collection_case_exercise_are_returned(context, ce):
    url = context.bdd_helper.threads_get_url + f"?ce={ce}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("user accesses the /health endpoint with using the POST method")
def step_impl_access_endpoint_with_post_method(context):
    context.response = context.client.post(context.bdd_helper.health_endpoint)


@when("user accesses the /health endpoint with using the PUT method")
def step_impl_access_endpoint_with_put_method(context):
    context.response = context.client.put(context.bdd_helper.health_endpoint)


@when("user accesses the /health/db endpoint with using the POST method")
def step_impl_access_health_db_endpoint_with_post_method(context):
    context.response = context.client.post(context.bdd_helper.health_db_endpoint)


@when("user accesses the /health/db endpoint with using the PUT method")
def step_impl_access_health_db_endpoint_with_put_method(context):
    context.response = context.client.put(context.bdd_helper.health_db_endpoint)


@when("user accesses the /health/details endpoint with using the PUT method")
def step_impl_access_health_details_endpoint_with_put_method(context):
    context.response = context.client.put(context.bdd_helper.health_details_endpoint)


@when("user accesses the /health/details endpoint with using the POST method")
def step_impl_access_health_details_endpoint_with_post_method(context):
    context.response = context.client.post(context.bdd_helper.health_details_endpoint)


@when("user accesses the /message/id endpoint with using the POST method")
def step_impl_access_message_id_endpoint_with_post_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.post(context.bdd_helper.message_get_url,
                                           data=json.dumps(context.bdd_helper.message_data),
                                           headers=context.bdd_helper.headers)


@when("user accesses the /message/id endpoint with using the PUT method")
def step_impl_access_message_id_endpoint_with_put_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.put(context.bdd_helper.message_get_url,
                                          data=json.dumps(context.bdd_helper.message_data),
                                          headers=context.bdd_helper.headers)


@when("user accesses the /message/id/modify endpoint with using the GET method")
def step_impl_access_message_id_endpoint_with_get_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.get(context.bdd_helper.message_put_url,
                                          data=json.dumps(context.bdd_helper.message_data),
                                          headers=context.bdd_helper.headers)


@when("user accesses the /message/id/modify endpoint with using the POST method")
def step_impl_access_message_id_modify_endpoint_with_post_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.post(context.bdd_helper.message_put_url,
                                           data=json.dumps(context.bdd_helper.message_data),
                                           headers=context.bdd_helper.headers)


@when("user accesses the /message/send endpoint with using the PUT method")
def step_impl_access_message_send_endpoint_with_put_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.put(context.bdd_helper.message_post_url,
                                          data=json.dumps(context.bdd_helper.message_data),
                                          headers=context.bdd_helper.headers)


@when("user accesses the /messages endpoint with using the PUT method")
def step_impl_access_messages_endpoint_with_wrong_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.put(context.bdd_helper.messages_get_url,
                                          data=json.dumps(context.bdd_helper.message_data),
                                          headers=context.bdd_helper.headers)


@when("user accesses the /messages endpoint with using the POST method")
def step_impl_access_messages_endpoint_with_post_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.post(context.bdd_helper.messages_get_url,
                                           data=json.dumps(context.bdd_helper.message_data),
                                           headers=context.bdd_helper.headers)

# V2 steps below this


@given("the message is sent V2")
@when("the message is sent V2")
def step_impl_the_message_is_sent_v2(context):
    """sends the current message data to the message send endpoint"""
    context.bdd_helper.sent_messages.extend([copy.deepcopy(context.bdd_helper.message_data)])
    context.response = context.client.post(context.bdd_helper.message_post_v2_url,
                                           data=json.dumps(context.bdd_helper.message_data),
                                           headers=context.bdd_helper.headers)

    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("the message is read V2")
@when("the message is read V2")
def step_impl_the_previously_saved_message_is_retrieved_using_v2_endpoint(context):
    """reads message with the id saved in the context via the message get V2 endpoint"""
    url = context.bdd_helper.message_get_v2_url.format(context.msg_id)
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    returned_data = json.loads(context.response.data)
    _try_persist_msg_and_thread_id_to_context(context, returned_data)
    context.bdd_helper.store_last_single_message_response_data(context.response)


@given("'{message_count}' messages are sent using V2")
@when("'{message_count}' messages are sent using V2")
def step_impl_the_n_messages_are_sent_via_v2(context, message_count):
    """sends a defined number of messages"""
    for i in range(0, int(message_count)):
        step_impl_the_message_is_sent_v2(context)


@given("messages are read V2")
@when("messages are read V2")
def step_impl_messages_are_read_using_v2(context):
    """get a message list"""
    url = context.bdd_helper.messages_get_v2_url
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    context.bdd_helper.store_messages_response_data(response_data)


@given("messages with a label of  '{label_name}' are read using V2")
@when("messages with a label of  '{label_name}' are read using V2")
def step_impl_messages_are_read_with_specific_label_using_v2(context, label_name):
    """filter get messages to only return messages matching a specified label"""
    param = f"?label={label_name}"
    url = context.bdd_helper.messages_get_v2_url + param
    _step_impl_get_messages_with_filter(context, url)


@given("messages are read using survey of '{survey}'")
@when("messages are read using survey of '{survey}'")
def step_impl_messages_are_read_with_specific_survey(context, survey):
    """restrict messages in get messages to those with a specific survey"""
    param = f"?survey={survey}"
    url = context.bdd_helper.messages_get_url + param
    _step_impl_get_messages_with_filter(context, url)


@when("the count of  messages with '{label_name}' label in survey '{survey}' is made V2")
@given("the count of  messages with '{label_name}' label in survey '{survey}' is made V2")
def step_impl_the_messages_for_specific_survey_are_counted_for_survey(context, label_name, survey):
    """access the messages_count endpoint to get the count of unread messages"""
    url = context.bdd_helper.messages_get_unread_count_v2_url + f"?label={label_name}&survey={survey}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    label_count = json.loads(response_data)["total"]
    context.bdd_helper.label_count = label_count


@when("the count of messages with '{label_name}' label is made V2")
@given("the count of messages with '{label_name}' label is made V2")
def step_impl_the_unread_messages_are_counted(context, label_name):
    """access the messages_count endpoint to get the count of unread messages"""
    url = context.bdd_helper.messages_get_unread_count_v2_url + f"?label={label_name}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    label_count = json.loads(response_data)["total"]
    context.bdd_helper.label_count = label_count


@when("the message labels are modified V2")
@given("the message labels are modified V2")
def step_impl_the_message_labels_are_modified_v2(context):
    """update the labels on the messages identified by the context.msg_id"""
    step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id_v2(context, context.msg_id)


@when("the message labels are modified on msg id '{msg_id}' V2")
@given("the message labels are modified on msg id '{msg_id}' V2")
def step_impl_the_specific_message_id_is_retrieved_on_specific_msg_id_v2(context, msg_id):
    """modify the labels on a specified message id"""
    url = context.bdd_helper.message_put_v2_url.format(msg_id)

    context.response = context.client.put(url, data=json.dumps(context.bdd_helper.message_data),
                                          headers=context.bdd_helper.headers)
    context.bdd_helper.store_last_single_message_response_data(context.response)
