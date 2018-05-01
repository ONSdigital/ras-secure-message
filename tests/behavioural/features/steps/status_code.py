import nose.tools
from behave import then


@then('a success status code 200 is returned')
def step_impl_200_success_returned(context):
    """validate that the status code was 200"""
    nose.tools.assert_equal(context.response.status_code, 200)


@then('a created status code 201 is returned')
def step_impl_201_success_returned(context):
    """validate that the status code was 201"""
    nose.tools.assert_equal(context.response.status_code, 201)


@then('a bad request status code 400 is returned')
def step_impl_a_bad_request_is_returned(context):
    """validate that the status code was 400"""
    nose.tools.assert_equal(context.response.status_code, 400)


@then("a forbidden status code (403) is returned")
def step_impl_403_returned(context):
    """validate that the status code was 403"""
    nose.tools.assert_equal(context.response.status_code, 403)


@then("a not found status code (404) is returned")
def step_impl_404_returned(context):
    """validate that the status code was 404"""
    nose.tools.assert_equal(context.response.status_code, 404)


@then("a not allowed status code (405) is returned")
def step_impl_405_returned(context):
    """validate that the status code was 405"""
    nose.tools.assert_equal(context.response.status_code, 405)


@then("a conflict error status code (409) is returned")
def step_impl_409_returned(context):
    """validate that the status code was 409"""
    nose.tools.assert_equal(context.response.status_code, 409)


@then("a '{status_code}' status code is returned")
def step_impl_status_code_returned(context, status_code):
    """validate that the status code was a specific value"""
    nose.tools.assert_equal(context.response.status_code, int(status_code))
