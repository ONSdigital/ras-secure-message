from behave import given, when


@given("the collection_exercise is set to '{collection_exercise}'")
@when("the collection_exercise is set to '{collection_exercise}'")
def step_impl_the_collection_exercise_is_set_to(context, collection_exercise):
    """set the collection exercise to a specific value"""
    context.bdd_helper.message_data['collection_exercise'] = collection_exercise
