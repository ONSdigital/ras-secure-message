import nose.tools
from behave import given, then, when


@given("an etag is requested with an empty value")
@when("an etag is requested with an empty value")
def step_impl_etag_is_requested_with_empty_value(context):
    """specify an etag but do not give it a value"""
    context.bdd_helper.headers["Etag"] = ""


@given("an etag is requested with a value of '{etag}'")
@when("an etag is requested with a value of '{etag}'")
def step_impl_etag_is_requested_with_specific_value(context, etag):
    """specify an etag of a specific value"""
    context.bdd_helper.headers["Etag"] = etag


@given("an etag is requested")
@when("an etag is requested")
def step_impl_etag_requested(context):
    """request an etag that matches the data to be sent"""
    etag_dict = context.bdd_helper.message_data
    etag_dict['msg_id'] = context.msg_id
    etag = context.bdd_helper.get_etag(etag_dict)
    step_impl_etag_is_requested_with_specific_value(context, etag)
