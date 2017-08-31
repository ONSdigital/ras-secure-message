import nose.tools
from behave import given, then, when


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