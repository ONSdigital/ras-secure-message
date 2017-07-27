import nose.tools
from app.application import app
from behave import given, then
from app.repository import database
from flask import current_app
from sqlalchemy.engine import Engine
from sqlalchemy import event


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


@then("an etag should be sent with the draft")
def step_impl_etag_should_be_sent_with_draft(context):
    etag = context.response.headers.get('ETag')
    nose.tools.assert_is_not_none(etag)
    nose.tools.assert_true(len(etag) == 40)


@then('a success status code (200) is returned')
def step_impl_success_returned(context):
    nose.tools.assert_equal(context.response.status_code, 200)


@then('a created status code (201) is returned')
def step_impl_success_returned(context):
    nose.tools.assert_equal(context.response.status_code, 201)

@then('a bad request status code (400) is returned')
def step_impl_a_bad_request_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@then("a not found status code (404) is returned")
def step_impl_conflict_returned(context):
    nose.tools.assert_equal(context.response.status_code, 404)

@then("a conflict error status code (409) is returned")
def step_impl_conflict_returned(context):
    nose.tools.assert_equal(context.response.status_code, 409)


@then("a '{status_code}' status code is returned")
def step_impl_status_code_returned(context, status_code):
    nose.tools.assert_equal(context.response.status_code, int(status_code))