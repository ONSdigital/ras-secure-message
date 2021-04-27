from behave import given, when


@given("the collection case is set to '{case_id}'")
@when("the collection case is set to '{case_id}'")
def step_impl_the_collection_case_is_set_to(context, case_id):
    """set the collection case field to a specific value"""
    context.bdd_helper.message_data['case_id'] = case_id
