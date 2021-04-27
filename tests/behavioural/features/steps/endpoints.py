import copy
import nose.tools

from behave import given, when, then
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


@when('the threads are read with my_conversations set true')
def step_impl_the_threads_are_read_with_my_conversations_set_true(context):
    url = context.bdd_helper.threads_get_url + "?my_conversations=true"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when('the threads are read with new_respondent_conversations set true')
def step_impl_the_threads_are_read_with_new_respondent_conversations_set_true(context):
    url = context.bdd_helper.threads_get_url + "?new_respondent_conversations=true"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads in survey '{survey_id}' are read")
@given("the threads in survey '{survey_id}' are read")
def step_impl_the_threads_in_specific_survey_are_returned(context, survey_id):
    url = context.bdd_helper.threads_get_url + f"?survey_id={survey_id}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads for business '{business_id}' in survey '{survey_id}' are read")
@given("the threads for business '{business_id}' in survey '{survey_id}' are read")
def step_impl_the_threads_in_specific_survey_and_business_are_returned(context, survey_id, business_id):
    url = context.bdd_helper.threads_get_url + f"?survey={survey_id}&business_id={business_id}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads in are read with filters for both default and alternate surveys")
def step_impl_the_threads_in_default_and_alternate_are_returned(context):
    url = context.bdd_helper.threads_get_url + f"?survey_id={context.bdd_helper.default_survey}" \
                                               f"&survey_id={context.bdd_helper.alternate_survey}"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    context.bdd_helper.store_messages_response_data(context.response.data)


@when("the threads with business_id '{business_id}' are read")
@given("the threads with business_id '{business_id}' are read")
def step_impl_the_threads_in_specific_business_id_are_returned(context, business_id):
    url = context.bdd_helper.threads_get_url + f"?business_id={business_id}"
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
    context.response = context.client.put(context.bdd_helper.messages_post_url,
                                          data=json.dumps(context.bdd_helper.message_data),
                                          headers=context.bdd_helper.headers)


@when("user accesses the /messages endpoint with using the POST method")
def step_impl_access_messages_endpoint_with_post_method(context):
    context.bdd_helper.sent_messages.extend([context.bdd_helper.message_data])
    context.response = context.client.post(context.bdd_helper.messages_post_url,
                                           data=json.dumps(context.bdd_helper.message_data),
                                           headers=context.bdd_helper.headers)


@when("the count of open threads in survey '{survey_id}'")
@given("the count of open threads in survey '{survey_id}'")
def step_impl_the_open_threads_count_for_specific_survey_are_counted(context, survey_id):
    """access the messages_count endpoint to get the count of unread conversations"""
    url = context.bdd_helper.threads_get_count_url + f"?survey_id={survey_id}&is_closed=false"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    context.bdd_helper.thread_count = json.loads(response_data)["total"]


@when("the count of open threads in default survey is made")
@given("the count of open threads in default survey is made")
def step_impl_the_open_threads_count_for_default_survey_are_counted(context):
    """access the messages_count endpoint to get the count of unread conversations"""
    url = context.bdd_helper.threads_get_count_url + f"?survey_id={context.bdd_helper.default_survey}&is_closed=false"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    context.bdd_helper.thread_count = json.loads(response_data)["total"]


@when("the count of open threads is made")
def step_impl_the_open_threads_count_are_counted(context):
    """access the messages_count endpoint to get the count of unread conversations"""
    url = context.bdd_helper.threads_get_count_url + "?is_closed=false"
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    context.bdd_helper.thread_count = json.loads(response_data)["total"]


@when("the count of open threads for current user is made")
@given("the count of open threads for current user is made")
def step_impl_my_open_threads_count_are_counted(context):
    """access the messages_count endpoint to get the count of my unread conversations"""
    url_args = "?is_closed=false&my_conversations=true"
    _step_impl_get_threads_count(context, url_args)


@when("the count of open threads for current user and ce of '{ce}' is made")
@given("the count of open threads for current user and ce of '{ce}' is made")
def step_impl_my_open_threads_count_are_counted_by_ce(context, ce):
    """access the messages_count endpoint to get the count of my unread conversations"""
    url_args = f"?is_closed=false&my_conversations=true&ce={ce}"
    _step_impl_get_threads_count(context, url_args)


@when("the count of open threads for current user and cc of '{cc}' is made")
@given("the count of open threads for current user and cc of '{cc}' is made")
def step_impl_my_open_threads_count_are_counted_by_cc(context, cc):
    """access the messages_count endpoint to get the count of my unread conversations"""
    url_args = f"?is_closed=false&my_conversations=true&cc={cc}"
    _step_impl_get_threads_count(context, url_args)


@when("the count of open threads for current user and business_id of '{business_id}' is made")
def step_impl_my_open_threads_count_are_counted_by_ru(context, business_id):
    """access the messages_count endpoint to get the count of my unread conversations"""
    url_args = f"?is_closed=false&my_conversations=true&business_id={business_id}"
    _step_impl_get_threads_count(context, url_args)


@when("the count of closed threads for current user is made")
@given("the count of closed threads for current user is made")
def step_impl_my_closed_threads_count_are_counted(context):
    url_args = "?is_closed=true&my_conversations=true"
    _step_impl_get_threads_count(context, url_args)


@when("the count of threads for new respondent conversations is made")
def step_impl_new_respondent_conversations_thread_count_are_counted(context):
    url_args = "?new_respondent_conversations=true"
    _step_impl_get_threads_count(context, url_args)


def _step_impl_get_threads_count(context, args):
    url = context.bdd_helper.threads_get_count_url + args
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    if context.response.status_code == 200:
        context.bdd_helper.thread_count = json.loads(response_data)["total"]
    else:
        context.bdd_helper.thread_count = -1


def _step_impl_get_threads_count_for_all_conversation_types(context, args):
    url = context.bdd_helper.threads_get_count_url + args
    context.response = context.client.get(url, headers=context.bdd_helper.headers)
    response_data = context.response.data
    if context.response.status_code == 200:
        context.bdd_helper.thread_counts_all_conversation_types = json.loads(response_data)["totals"]
    else:
        context.bdd_helper.thread_counts_all_conversation_types = None


@then("A count of '{count}' is returned")
def step_impl_the_return_count_is(context, count):
    nose.tools.assert_equal(count, context.bdd_helper.last_saved_message_data['msg_to'])


@when("the count of all conversation types closed threads for current user is made")
@given("the count of all conversation types closed threads for current user is made")
def step_impl_all_conversation_types_count_are_counted(context):
    """access the messages_count endpoint with all_conversation_types set"""
    url_args = "?all_conversation_types=true"
    _step_impl_get_threads_count_for_all_conversation_types(context, url_args)
