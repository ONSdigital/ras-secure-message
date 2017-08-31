import nose.tools
from app.application import app
from app.services.service_toggles import party, case_service
from behave import given, then, when
from app.repository import database
from flask import current_app, json
from sqlalchemy.engine import Engine
from sqlalchemy import event
from tests.behavioural.features.steps.bdd_test_helper import BddTestHelper
from app import constants


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """enable foreign key constraint for tests"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@given("database is reset")
def step_impl_reset_db(context):
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()
    context.bdd_helper = BddTestHelper()


@given("using mock party service")
def step_impl_use_mock_party_service(context):
    party.use_mock_service()


@given("using mock case service")
def step_impl_use_mock_case_service(service):
    case_service.use_mock_service()

#  -----   user operations -----

@given("new the user is set as internal")
@when("new the user is set as internal")
def step_impl_the_user_is_internal(context):
    context.bdd_helper.token_data = context.bdd_helper.internal_user_token


@given("new the user is set as alternative respondent")
@when("new the user is set as alternative respondent")
def step_impl_the_user_is_set_as_alternative_respondent(context):
    context.bdd_helper.token_data = context.bdd_helper.alternative_respondent_user_token


@given("new the user is set as respondent")
@when("new the user is set as respondent")
def step_impl_the_user_is_set_as_respondent(context):
    context.bdd_helper.token_data = context.bdd_helper.respondent_user_token


@given("new sending from respondent to internal")
@when("new sending from respondent to internal")
def step_impl_prepare_to_send_from_respondent(context):
    step_impl_the_user_is_set_as_respondent(context)
    step_impl_the_msg_from_is_set_to_respondent(context)
    step_impl_the_msg_to_is_set_to_internal(context)


@given("new sending from internal to respondent")
@when("new sending from internal to respondent")
def step_impl_prepare_to_send_from_respondent(context):
    step_impl_the_user_is_internal(context)
    step_impl_the_msg_from_is_set_to_internal(context)
    step_impl_the_msg_to_is_set_to_respondent(context)


#  -----   from field operations -----

@given("new the from is set to '{msg_from}'")
@when("new the from is set to '{msg_from}'")
def step_impl_the_msg_from_is_set_to(context, msg_from):
    context.bdd_helper.message_data['msg_from'] = msg_from


@given("new the from is set to empty")
@when("new the from is set to empty")
def step_impl_the_msg_from_is_set_to_empty(context):
    context.bdd_helper.message_data['msg_from'] = ''


@given("new the from is too long")
def step_impl_the_msg_from_is_set_too_long(context):
    context.bdd_helper.message_data['msg_from'] = "x" * (constants.MAX_FROM_LEN + 1)


@given("new the from is set to respondent")
@when("new the from is set to respondent")
def step_impl_the_msg_from_is_set_to_respondent(context):
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.respondent_id)


@given("new the from is set to alternative respondent")
@when("new the from is set to alternative respondent")
def step_impl_the_msg_from_is_set_to_alternative_respondent(context):
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.alternative_respondent_id)


@given("new the from is set to internal")
@when("new the from is set to internal")
def step_impl_the_msg_from_is_set_to_internal(context):
    step_impl_the_msg_from_is_set_to(context, context.bdd_helper.internal_id)

#  -----   to field operations -----


@given("new the to is set to '{msg_to}'")
@when("new the to is set to '{msg_to}'")
def step_impl_the_msg_to_is_set_to(context, msg_to):
    context.bdd_helper.message_data['msg_to'][0] = msg_to


@given("new the to is set to empty")
@when("new the to is set to empty")
def step_impl_the_msg_to_is_set_to_empty(context):
    context.bdd_helper.message_data['msg_to'][0] = ''


@given("new the to field is too long")
def step_impl_the_msg_to_is_set_too_long(context):
    context.bdd_helper.message_data['msg_to'][0] = "x" * (constants.MAX_TO_LEN+1)


@given("new the to is set to respondent")
@when("new the to is set to respondent")
def step_impl_the_msg_to_is_set_to_respondent(context):
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.respondent_id)


@given("new the to is set to alternative respondent")
@when("new the to is set to alternative respondent")
def step_impl_the_msg_to_is_set_to_alternative_respondent(context):
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.alternative_respondent_id)


@given("new the to is set to internal")
@when("new the to is set to internal")
def step_impl_the_msg_to_is_set_to_internal(context):
    step_impl_the_msg_to_is_set_to(context, context.bdd_helper.internal_id)


@given("new the to is set to respondent as a string not array")
@when("new the to is set to respondent as a string not array")
def step_impl_the_msg_to_is_set_to_respondent_as_string_not_array(context):
    context.bdd_helper.message_data['msg_to']=context.bdd_helper.respondent_id


@given("new the to is set to internal user as a string not array")
@when("new the to is set to internal user as a string not array")
def step_impl_the_msg_to_is_set_to_internal_as_string_not_array(context):
    context.bdd_helper.message_data['msg_to'] = context.bdd_helper.internal_id

#  -----   msg_id field operations -----


@given("new the msg_id is set to '{msg_id}'")
@when("new the msg_id is set to '{msg_id}'")
def step_impl_the_msg_id_is_set_to(context, msg_id):
    context.bdd_helper.message_data['msg_id'] = msg_id
    context.msg_id = msg_id


#  -----   thread id field operations -----

@given("new the thread_id is set to '{thread_id}'")
@when("new the thread_id is set to '{thread_id}'")
def step_impl_the_thread_id_is_set_to(context, thread_id):
    context.bdd_helper.message_data['thread_id'] = thread_id


@given("new the thread id is set to the last returned thread id")
@when("new the thread id is set to the last returned thread id")
def step_impl_the_thread_id_is_set_to_the_last_returned_thread_id(context):
    responses = context.bdd_helper.responses_data
    thread_id = responses[len(responses)-1]['thread_id']
    context.bdd_helper.message_data['thread_id'] = thread_id


@then("new the thread id is equal in all responses")
def step_impl_the_thread_id_is_set_to_the_last_returned_thread_id(context):
    responses = context.bdd_helper.responses_data
    last_thread_id = responses[len(responses)-1]['thread_id']
    for response in responses:
        nose.tools.assert_equals(response['thread_id'], last_thread_id)




#  -----   survey field operations -----


@given("new the survey is set to '{survey}'")
@when("new the survey is set to '{survey}'")
def step_impl_the_survey_is_set_to(context, survey):
    context.bdd_helper.message_data['survey'] = survey


@given("new the survey is set to empty")
@when("new the survey is set to empty")
def step_impl_the_survey_is_set_to_empty(context):
    context.bdd_helper.message_data['survey'] = ''

#  -----   body field operations -----


@given("new the body is set to '{body}'")
@when("new the body is set to '{body}'")
def step_impl_the_body_is_set_to(context, body):
    context.bdd_helper.message_data['body'] = body


@given("new the body is set to include an apostrophe")
@when("new the body is set to include an apostrophe")
def step_impl_the_body_is_set_to(context):
    context.bdd_helper.message_data['body'] = "A body including ' an apostrophe"


@given("new the body is set to empty")
@when("new the body is set to empty")
def step_impl_the_body_is_set_to_empty(context):
    context.bdd_helper.message_data['body'] = ''


@given("new the body is too long")
def step_impl_the_msg_body_is_set_too_long(context):
    context.bdd_helper.message_data['body'] = "x" * (constants.MAX_BODY_LEN + 1)

#  -----   subject field operations -----


@given("new the subject is set to '{body}'")
@when("new the subject is set to '{body}'")
def step_impl_the_subject_is_set_to(context, subject):
    context.bdd_helper.message_data['subject'] = subject


@given("new the subject is set to empty")
@when("new the subject is set to empty")
def step_impl_the_subject_is_set_to_empty(context):
    context.bdd_helper.message_data['subject'] = ''


@given("new the subject is too long")
def step_impl_the_msg_subject_is_set_too_long(context):
    context.bdd_helper.message_data['subject'] = "x" * (constants.MAX_SUBJECT_LEN + 1)

#  -----   collection case field operations -----


@given("new the collection case is set to '{collection_case}'")
@when("new the collection case is set to '{collection_case}'")
def step_impl_the_collection_case_is_set_to(context, collection_case):
    context.bdd_helper.message_data['collection_case'] = collection_case


@given("new the collection case is too long")
def step_impl_the_msg_collection_case_is_set_too_long(context):
    context.bdd_helper.message_data['collection_case'] = "x" * (constants.MAX_COLLECTION_CASE_LEN + 1)


@given("new the collection exercise is too long")
def step_impl_the_msg_collection_exercise_is_set_too_long(context):
    context.bdd_helper.message_data['collection_exercise'] = "x" * (constants.MAX_COLLECTION_EXERCISE_LEN + 1)

#  -----   collection exercise field operations -----


@given("new the collection_exercise is set to '{collection_exercise}'")
@when("new the collection_exercise is set to '{collection_exercise}'")
def step_impl_the_collection_exercise_is_set_to(context, collection_exercise):
    context.bdd_helper.message_data['collection_exercise'] = collection_exercise

#  -----   ru field operations -----


@given("new the ru is set to '{ru}'")
@when("new the ru is set to '{ru}'")
def step_impl_the_ru_is_set_to(context, ru):
    context.bdd_helper.message_data['ru'] = ru

#  -----   accessing endpoints -----


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
    url = context.bdd_helper.draft_put_url.format(context.msg_id)
    sent_data = context.bdd_helper.message_data
    sent_data['msg_id'] = context.msg_id            # draft put requires msg_id
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

#  -----   status code validations and response data -----


@then('a success status code (200) is returned')
def step_impl_success_returned(context):
    nose.tools.assert_equal(context.response.status_code, 200)


@then('a created status code (201) is returned')
def step_impl_success_returned(context):
    nose.tools.assert_equal(context.response.status_code, 201)


@then('a bad request status code (400) is returned')
def step_impl_a_bad_request_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@then("a forbidden status code (403) is returned")
def step_impl_conflict_returned(context):
    nose.tools.assert_equal(context.response.status_code, 403)


@then("a not found status code (404) is returned")
def step_impl_conflict_returned(context):
    nose.tools.assert_equal(context.response.status_code, 404)


@then("a conflict error status code (409) is returned")
def step_impl_conflict_returned(context):
    nose.tools.assert_equal(context.response.status_code, 409)


@then("a '{status_code}' status code is returned")
def step_impl_status_code_returned(context, status_code):
    nose.tools.assert_equal(context.response.status_code, int(status_code))


@then("new response includes a msg_id")
def step_impl_response_includes_msg_id(context ):
    returned_data = json.loads(context.response.data)
    nose.tools.assert_true('msg_id' in returned_data)
    nose.tools.assert_true(len(returned_data['msg_id']) == 36)


#  -----   field validations -----


@then("new the response message has the label '{label}'")
def step_impl_the_response_message_should_have_named_label(context, label):
    response = json.loads(context.response.data)
    nose.tools.assert_true(label in response['labels'])


@then("new the response message does not have the label '{label}'")
def step_impl_the_response_message_should_not_have_named_label(context, label):
    response = json.loads(context.response.data)
    nose.tools.assert_false(label in response['labels'])


@then("new the response message should a label count of '{label_count}'")
def step_impl_the_response_message_should_have_named_label(context, label_count):
    response = json.loads(context.response.data)
    nose.tools.assert_equals(len(response['labels']), int(label_count))


@then("new retrieved message thread id is equal to message id")
def step_impl_the_response_message_thread_id_equals_the_message_id(context):
    response = json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['thread_id'])
    nose.tools.assert_equal(response['thread_id'], response['msg_id'])


@then("new retrieved message thread id is not equal to message id")
def step_impl_the_response_message_thread_id_not_equal_to_the_message_id(context):
    response = json.loads(context.response.data)
    nose.tools.assert_is_not_none(response['thread_id'])
    nose.tools.assert_not_equal(response['thread_id'], response['msg_id'])


@then("new retrieved message msg_to is as was saved")
def step_impl_retrieved_msg_to_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_to'], context.bdd_helper.last_saved_message_data['msg_to'])


@then("new retrieved message msg_from is as was saved")
def step_impl_retrieved_msg_from_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['msg_from'], context.bdd_helper.last_saved_message_data['msg_from'])


@then("new retrieved message body is as was saved")
def step_impl_retrieved_body_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['body'], context.bdd_helper.last_saved_message_data['body'])


@then("new retrieved message subject is as was saved")
def step_impl_retrieved_subject_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['subject'], context.bdd_helper.last_saved_message_data['subject'])


@then("new retrieved message ru is as was saved")
def step_impl_retrieved_ru_id_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['ru_id'], context.bdd_helper.last_saved_message_data['ru_id'])


@then("new retrieved message collection case is as was saved")
def step_impl_retrieved_collection_case_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_case'], context.bdd_helper.last_saved_message_data['collection_case'])


@then("new retrieved message collection exercise is as was saved")
def step_impl_retrieved_collection_exercise_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['collection_exercise'],
                            context.bdd_helper.last_saved_message_data['collection_exercise'])


@then("new retrieved message survey is as was saved")
def step_impl_retrieved_survey_is_as_saved(context):
    msg_resp = json.loads(context.response.data)
    nose.tools.assert_equal(msg_resp['survey'], context.bdd_helper.last_saved_message_data['survey'])


@given("new using the '{message_index}' message ")
@when("new using the '{message_index}' message ")
def step_impl_reuse_the_nth_sent_message(context, message_index):
    context.bdd_helper.set_message_data_to_a_prior_version(message_index)


@then("new retrieved message additional from data matches that from party service")
def step_impl_verify_additional_from_data_matches_that_from_party_service(context):
    msg_resp = json.loads(context.response.data)
    party_data, party_status = party.get_user_details(msg_resp['msg_from'])
    nose.tools.assert_equal(msg_resp['@msg_from'], party_data)


@then("new retrieved message additional to data matches that from party service")
def step_impl_verify_additional_to_data_matches_that_from_party_service(context):
    msg_resp = json.loads(context.response.data)
    party_data, party_status = party.get_user_details(msg_resp['msg_to'][0])
    nose.tools.assert_equal(msg_resp['@msg_to'][0], party_data)


@then("new retrieved message additional ru_id data matches that from party service")
def step_impl_verify_additional_to_data_matches_that_from_party_service(context):
    msg_resp = json.loads(context.response.data)
    party_data, party_status = party.get_business_details(msg_resp['ru_id'])
    nose.tools.assert_equal(msg_resp['@ru_id'], party_data)


# -----  etag operations -----

@then("new the response should include a valid etag")
def step_impl_etag_should_be_sent_with_draft(context):
    etag = context.response.headers.get('ETag')
    nose.tools.assert_is_not_none(etag)
    nose.tools.assert_equal(len(etag), 40)


@given("new an etag is requested with an empty value")
@when("new an etag is requested with an empty value")
def step_impl_etag_is_requested(context):
    context.bdd_helper.headers["Etag"] = ""


@given("new an etag is requested with a value of '{etag}'")
@when("new an etag is requested with a value of '{etag}'")
def step_impl_etag_is_requested(context, etag):
    context.bdd_helper.headers["Etag"] = etag


@given("new an etag is requested")
@when("new an etag is requested")
def step_impl_etag_requested(context):
    etag_dict = context.bdd_helper.message_data
    etag_dict['msg_id'] = context.msg_id
    etag = context.bdd_helper.get_etag(etag_dict)
    step_impl_etag_is_requested(context, etag)


@then("an etag should be sent with the draft")
def step_impl_etag_should_be_sent_with_draft(context):
    etag = context.response.headers.get('ETag')
    nose.tools.assert_is_not_none(etag)
    nose.tools.assert_true(len(etag) == 40)

# ----- Label operations -----
@given("new a label of '{label}' is to be added")
@when("new a label of '{label}' is to be added")
def step_impl_a_named_label_is_to_be_added(context, label):
    context.bdd_helper.message_data={"action": "add", "label": label}


@given("new a label of '{label}' is to be removed")
@when("new a label of '{label}' is to be removed")
def step_impl_a_named_label_is_to_be_removed(context, label):
    context.bdd_helper.message_data={"action": "remove", "label": label}


@given("new a label of '{label}' has unknown action")
@when("new a label of '{label}' has unknown action")
def step_impl_a_named_label_is_to_be_removed(context, label):
    context.bdd_helper.message_data={"action": "some_unknown_action", "label": label}

# ----- recovering messages sent earlier operations -----


# Feature files do not support breakpoints , but you may add a debug step and put a breakpoint on the pass below


@given("A debug step")
@when("A debug step")
@then("A debug step")
def step_impl_no_op(context):
    pass
