from behave import given, when
from tests.behavioural.features.steps.from_field_steps import step_impl_the_msg_from_is_set_to_respondent,\
                                                              step_impl_the_msg_from_is_set_to_internal
from tests.behavioural.features.steps.to_field_steps import step_impl_the_msg_to_is_set_to_internal,\
                                                              step_impl_the_msg_to_is_set_to_respondent
from app import constants


@given("new the user is set as internal")
@when("new the user is set as internal")
def step_impl_the_user_is_internal(context):
    context.bdd_helper.token_data = context.bdd_helper.internal_user_token


@given("new the user is set as alternative respondent")
@when("new the user is set as alternative respondent")
def step_impl_the_user_is_set_as_alternative_respondent(context):
    context.bdd_helper.token_data = context.bdd_helper.alternative_respondent_user_token


@given("new the user is set as respondent")
@when("new the user is set as respondent")
def step_impl_the_user_is_set_as_respondent(context):
    context.bdd_helper.token_data = context.bdd_helper.respondent_user_token


@given("new sending from respondent to internal")
@when("new sending from respondent to internal")
def step_impl_prepare_to_send_from_respondent(context):
    step_impl_the_user_is_set_as_respondent(context)
    step_impl_the_msg_from_is_set_to_respondent(context)
    step_impl_the_msg_to_is_set_to_internal(context)


@given("new sending from internal to respondent")
@when("new sending from internal to respondent")
def step_impl_prepare_to_send_from_respondent(context):
    step_impl_the_user_is_internal(context)
    step_impl_the_msg_from_is_set_to_internal(context)
    step_impl_the_msg_to_is_set_to_respondent(context)


@given("the user token is set to respondent with no user id")
@when("the user token is set to respondent with no user id")
def step_impl_set_token_directly(context):
    context.bdd_helper.token_data = {constants.USER_IDENTIFIER: "", "role": "respondent"}


@given("the user token is set to internal with no user id")
@when("the user token is set to internal with no user id")
def step_impl_set_token_directly(context):
    context.bdd_helper.token_data = {constants.USER_IDENTIFIER: "", "role": "internal"}


