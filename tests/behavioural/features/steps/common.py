import nose.tools
from behave import given, then, when

from secure_message.repository import database
from secure_message.services.service_toggles import internal_user_service, party
from tests.behavioural.features.steps.secure_messaging_context_helper import (
    SecureMessagingContextHelper,
)


@given("prepare for tests using '{service_type}' services")
def step_impl_prepare_for_tests(context, service_type):
    """Prepare bdd tests to run against either mock or real external services."""
    step_impl_reset_db(context)
    with context.app.app_context():
        context.bdd_helper = SecureMessagingContextHelper()
    if service_type.lower() == "real":
        party.use_real_service()
        internal_user_service.use_real_service()
    else:
        party.use_mock_service()
        internal_user_service.use_mock_service()


@given("database is reset")
def step_impl_reset_db(context):
    """Reset database and use the context test helper."""
    with context.app.app_context():
        database.db.drop_all()
        database.db.create_all()


@given("using mock party service")
def step_impl_use_mock_party_service(context):
    """Use mock party service tests."""
    party.use_mock_service()


@given("using mock internal user service")
def step_impl_use_mock_internal_user_service(context):
    """Use mock internal user service tests."""
    internal_user_service.use_mock_service()


@given("using the '{message_index}' message")
@when("using the '{message_index}' message")
def step_impl_reuse_the_nth_sent_message(context, message_index):
    """Switch to using the data from a previously sent message."""
    context.bdd_helper.set_message_data_to_a_prior_version(int(message_index))


@then("'{message_count}' messages are returned")
def step_impl_n_messages_returned(context, message_count):
    """Validate that the correct number of messages was returned."""
    nose.tools.assert_equal(int(message_count), len(context.bdd_helper.messages_responses_data[0]["messages"]))


@then("the thread count is '{thread_count}' threads")
def step_impl_thread_count_validate(context, thread_count):
    nose.tools.assert_equal(int(thread_count), context.bdd_helper.thread_count)


@then("the thread open count is '{thread_count}' threads")
def step_impl_open_thread_count_validate(context, thread_count):
    nose.tools.assert_equal(int(thread_count), context.bdd_helper.thread_counts_all_conversation_types["open"])


@then("the thread closed count is '{thread_count}' threads")
def step_impl_closed_thread_count_validate(context, thread_count):
    nose.tools.assert_equal(int(thread_count), context.bdd_helper.thread_counts_all_conversation_types["closed"])


@then("the thread my_conversations count is '{thread_count}' threads")
def step_impl_my_conversations_thread_count_validate(context, thread_count):
    nose.tools.assert_equal(
        int(thread_count), context.bdd_helper.thread_counts_all_conversation_types["my_conversations"]
    )


@then("the thread new_respondent_conversations count is '{thread_count}' threads")
def step_impl_new_respondent_conversations_thread_count_validate(context, thread_count):
    nose.tools.assert_equal(
        int(thread_count), context.bdd_helper.thread_counts_all_conversation_types["new_respondent_conversations"]
    )


@given("debug step")
@when("debug step")
@then("debug step")
def step_impl_debug_step(context):
    """Allows a debug step to be set in a feature file by break pointing the pass below."""
    pass
