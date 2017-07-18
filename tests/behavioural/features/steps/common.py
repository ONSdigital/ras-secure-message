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


@then('a success response is given')
def step_impl_success_returned(context):
    nose.tools.assert_equal(context.response.status_code, 200)


@then('a bad request error is returned')
def step_impl_a_bad_request_is_returned(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@then("a 404 error code is returned")
def step_impl_404_returned(context):
    nose.tools.assert_equal(context.response.status_code, 404)