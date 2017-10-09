from app.application import app
from app.services.service_toggles import party, case_service
from behave import given, then, when
from app.repository import database
from flask import current_app
from sqlalchemy.engine import Engine
from sqlalchemy import event
from tests.behavioural.features.steps.secure_messaging_context_helper import SecureMessagingContextHelper


import nose.tools


@given("prepare for tests using '{service_type}' services")
def step_impl_prepare_for_tests(context, service_type):
    """Prepare bdd tests to run against either mock or real external services"""
    step_impl_reset_db(context)
    context.bdd_helper = SecureMessagingContextHelper()
    if service_type.lower() == 'real':
        party.use_real_service()
        case_service.use_real_service()
    else:
        party.use_mock_service()
        case_service.use_mock_service()


@given("database is reset")
def step_impl_reset_db(context):
    """ reset database and use the context test helper"""
    with app.app_context():
        database.db.init_app(current_app)
        database.db.drop_all()
        database.db.create_all()
    context.sm_context_helper = SecureMessagingContextHelper()


@given("using mock party service")
def step_impl_use_mock_party_service(context):
    """ use the default party service tests"""
    party.use_mock_service()


@given("using mock case service")
def step_impl_use_mock_case_service(context):
    """ Use mock case service"""
    case_service.use_mock_service()


@given("using the '{message_index}' message")
@when("using the '{message_index}' message")
def step_impl_reuse_the_nth_sent_message(context, message_index):
    """ switch to using the data from a previously sent message """
    context.bdd_helper.set_message_data_to_a_prior_version(int(message_index))


@then("'{message_count}' messages are returned")
def step_impl_n_messages_returned(context, message_count):
    """ validate that the correct number of messages was returned"""
    nose.tools.assert_equal(int(message_count), len(context.bdd_helper.messages_responses_data[0]['messages']))


# Feature files do not support breakpoints , but you may add a debug step and put a breakpoint on the pass below


@given("A debug step")
@when("A debug step")
@then("A debug step")
def step_impl_no_op(context):
    """Useful in debugging feature files"""
    pass
