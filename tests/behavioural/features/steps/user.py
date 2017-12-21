from behave import given, when
from tests.behavioural.features.steps.from_field import step_impl_the_msg_from_is_set_to_respondent,\
                                                              step_impl_the_msg_from_is_set_to_internal
from tests.behavioural.features.steps.to_field import step_impl_the_msg_to_is_set_to_internal,\
                                                              step_impl_the_msg_to_is_set_to_respondent
from secure_message import constants


@given("the user is set as internal")
@when("the user is set as internal")
def step_impl_the_user_is_internal(context):
    """Set the user to the internal user"""
    context.bdd_helper.token_data = context.bdd_helper.internal_user_token


@given("the user is set as alternative respondent")
@when("the user is set as alternative respondent")
def step_impl_the_user_is_set_as_alternative_respondent(context):
    """ Set the user to the alternative respondent as set in the helper"""
    context.bdd_helper.token_data = context.bdd_helper.alternative_respondent_user_token


@given("the user is set as respondent")
@when("the user is set as respondent")
def step_impl_the_user_is_set_as_respondent(context):
    """set the user to the default respondent as saved in the helper"""
    context.bdd_helper.token_data = context.bdd_helper.respondent_user_token


@given("sending from respondent to internal")
@when("sending from respondent to internal")
def step_impl_prepare_to_send_from_respondent(context):
    """set the message from to the internal user as defined in the helper"""
    step_impl_the_user_is_set_as_respondent(context)
    step_impl_the_msg_from_is_set_to_respondent(context)
    step_impl_the_msg_to_is_set_to_internal(context)


@given("sending from internal to respondent")
@when("sending from internal to respondent")
def step_impl_prepare_to_send_from_respondent(context):
    """ set the from to the repondent as set in the helper"""
    step_impl_the_user_is_internal(context)
    step_impl_the_msg_from_is_set_to_internal(context)
    step_impl_the_msg_to_is_set_to_respondent(context)


@given("the user token is set to respondent with no user id")
@when("the user token is set to respondent with no user id")
def step_impl_set_token_directly(context):
    """set the user token to be a respondent but have no user id"""
    context.bdd_helper.token_data = {constants.USER_IDENTIFIER: "", "role": "respondent"}


@given("the user token is set to internal with no user id")
@when("the user token is set to internal with no user id")
def step_impl_set_token_directly(context):
    """set the user token to an internal user withno user id"""
    context.bdd_helper.token_data = {constants.USER_IDENTIFIER: "", "role": "internal"}


@given("the user token is set to a respondent with no role associated")
@when("the user token is set to a respondent with no role associated")
def step_impl_set_token_with_no_role(context):
    context.bdd_helper.token_data = {constants.USER_IDENTIFIER: context.bdd_helper.respondent_id, "role": ""}


@given("the user token is set to a internal user with no role associated")
@when("the user token is set to a internal user with no role associated")
def step_impl_set_token_with_no_role(context):
    context.bdd_helper.token_data = {constants.USER_IDENTIFIER: context.bdd_helper.internal_id, "role": ""}
