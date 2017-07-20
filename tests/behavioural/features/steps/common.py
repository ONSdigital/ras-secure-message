from app.application import app
from behave import given, when, then
from app.repository import database
from flask import current_app

import nose.tools


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


@then('a success response is given')
def step_impl_success_returned(context):
    nose.tools.assert_equal(context.response.status_code, 200)


@then('a 201 status code is the response')
def step_impl_201_returned(context):
    nose.tools.assert_equal(context.response.status_code, 201)


@then('a bad request error is returned')
def step_impl_a_bad_request_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@then("a 404 error code is returned")
def step_impl_404_returned(context):
    nose.tools.assert_equal(context.response.status_code, 404)


@then("a conflict error is returned")
def step_impl_conflict_returned(context):
    nose.tools.assert_equal(context.response.status_code, 409)
