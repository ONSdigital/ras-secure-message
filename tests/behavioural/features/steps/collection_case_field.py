from behave import given, when


@given("the collection case is set to '{collection_case}'")
@when("the collection case is set to '{collection_case}'")
def step_impl_the_collection_case_is_set_to(context, collection_case):
    """set the collection case field to a specific value"""
    context.bdd_helper.message_data['collection_case'] = collection_case
