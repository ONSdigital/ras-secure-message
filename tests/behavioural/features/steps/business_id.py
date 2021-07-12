from behave import given, when


@given("the business_id is set to '{business_id}'")
@when("the business_id is set to '{business_id}'")
def step_impl_the_ru_is_set_to(context, business_id):
    """set the message data business_id to a specific value"""
    context.bdd_helper.message_data["business_id"] = business_id
