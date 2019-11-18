from behave import given, when


@given("the subject is set to '{subject}'")
@when("the subject is set to '{subject}'")
def step_impl_the_subject_is_set_to(context, subject):
    """set the subject field in message data to a specific value"""
    context.bdd_helper.message_data['subject'] = subject


@given("the subject is set to empty")
@when("the subject is set to empty")
def step_impl_the_subject_is_set_to_empty(context):
    """set the subject field in message data to be empty"""
    context.bdd_helper.message_data['subject'] = ''
