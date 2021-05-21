from behave import given, when


@given("the collection_exercise is set to '{exercise_id}'")
@when("the collection_exercise is set to '{exercise_id}'")
def step_impl_the_collection_exercise_is_set_to(context, exercise_id):
    """set the collection exercise to a specific value"""
    context.bdd_helper.message_data['exercise_id'] = exercise_id
