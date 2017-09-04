import nose.tools
from behave import given, then, when


@then("the response should include a valid etag")
def step_impl_etag_should_be_sent_with_draft(context):
    """validate that an etag of the correct length is in the response"""
    etag = context.response.headers.get('ETag')
    nose.tools.assert_is_not_none(etag)
    nose.tools.assert_equal(len(etag), 40)


@given("an etag is requested with an empty value")
@when("an etag is requested with an empty value")
def step_impl_etag_is_requested(context):
    """specify an etag but do not give it a value"""
    context.bdd_helper.headers["Etag"] = ""


@given("an etag is requested with a value of '{etag}'")
@when("an etag is requested with a value of '{etag}'")
def step_impl_etag_is_requested(context, etag):
    """specify an etag ofa specificvalue"""
    context.bdd_helper.headers["Etag"] = etag


@given("an etag is requested")
@when("an etag is requested")
def step_impl_etag_requested(context):
    """request an etag that matches the data to be sent"""
    etag_dict = context.bdd_helper.message_data
    etag_dict['msg_id'] = context.msg_id
    etag = context.bdd_helper.get_etag(etag_dict)
    step_impl_etag_is_requested(context, etag)
