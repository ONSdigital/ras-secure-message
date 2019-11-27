from behave import given, when


@given("the msg_id is set to '{msg_id}'")
@when("the msg_id is set to '{msg_id}'")
def step_impl_the_msg_id_is_set_to(context, msg_id):
    """set the message data messge id to a specific value"""
    context.bdd_helper.message_data['msg_id'] = msg_id
    context.msg_id = msg_id
