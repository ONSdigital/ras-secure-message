from app.application import app
from app.services.service_toggles import party, case_service
from behave import given, then, when
from app.repository import database
from flask import current_app, json
from sqlalchemy.engine import Engine
from sqlalchemy import event
from tests.behavioural.features.steps.bdd_test_helper import BddTestHelper


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
def step_impl_use_mock_case_service(context):
    case_service.use_mock_service()


@given("new using the '{message_index}' message ")
@when("new using the '{message_index}' message ")
def step_impl_reuse_the_nth_sent_message(context, message_index):
    context.bdd_helper.set_message_data_to_a_prior_version(message_index)


# Feature files do not support breakpoints , but you may add a debug step and put a breakpoint on the pass below


@given("A debug step")
@when("A debug step")
@then("A debug step")
def step_impl_no_op(context):
    pass
