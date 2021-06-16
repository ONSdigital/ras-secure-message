from behave import given, when


@given("the msg_category is set to '{msg_category}'")
@when("the msg_category is set to '{msg_category}'")
def step_impl_the_msg_id_is_set_to(context, msg_category):
    """set the message data messge id to a specific value"""
    context.bdd_helper.message_data['msg_category'] = msg_category
    context.msg_category = msg_category
