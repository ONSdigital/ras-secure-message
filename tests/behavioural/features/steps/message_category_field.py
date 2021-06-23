from behave import given, when


@given("the category is set to '{category}'")
@when("the category is set to '{category}'")
def step_impl_the_msg_id_is_set_to(context, category):
    """set the message data messge id to a specific value"""
    context.bdd_helper.message_data['category'] = category
    context.category = category
