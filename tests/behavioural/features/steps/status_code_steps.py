import nose.tools
from behave import then


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

