from behave import given, when
from tests.behavioural.features.steps.from_field import step_impl_the_msg_from_is_set_to_respondent
from tests.behavioural.features.steps.from_field import step_impl_the_msg_from_is_set_to_internal_bres_user
from tests.behavioural.features.steps.from_field import step_impl_the_msg_from_is_set_to_internal_specific_user
from tests.behavioural.features.steps.from_field import step_impl_the_msg_from_is_set_to_internal_group_user

from tests.behavioural.features.steps.to_field import step_impl_the_msg_to_is_set_to_internal_bres_user
from tests.behavioural.features.steps.to_field import step_impl_the_msg_to_is_set_to_respondent
from tests.behavioural.features.steps.to_field import step_impl_the_msg_to_is_set_to_internal_group_user
from tests.behavioural.features.steps.to_field import step_impl_the_msg_to_is_set_to_internal_specific_user
from secure_message import constants


@given("the user is set as internal")
@when("the user is set as internal")
def step_impl_the_user_is_internal(context):
    """Set the user to the internal user"""
    with context.app.app_context():
        context.bdd_helper.token_data = context.bdd_helper.internal_bres_user_token


@given("the user is set as alternative respondent")
@when("the user is set as alternative respondent")
def step_impl_the_user_is_set_as_alternative_respondent(context):
    """ Set the user to the alternative respondent as set in the helper"""
    with context.app.app_context():
        context.bdd_helper.token_data = context.bdd_helper.alternative_respondent_user_token


@given("the user is set as respondent")
@when("the user is set as respondent")
def step_impl_the_user_is_set_as_respondent(context):
    """set the user to the default respondent as saved in the helper"""
    with context.app.app_context():
        context.bdd_helper.token_data = context.bdd_helper.respondent_user_token


@given("sending from respondent to internal bres user")
@when("sending from respondent to internal bres user")
def step_impl_prepare_to_send_from_respondent_to_bres_user(context):
    """set the message from to the internal user as defined in the helper"""
    step_impl_the_user_is_set_as_respondent(context)
    step_impl_the_msg_from_is_set_to_respondent(context)
    step_impl_the_msg_to_is_set_to_internal_bres_user(context)


@given("sending from internal bres user to respondent")
@when("sending from internal bres user to respondent")
def step_impl_prepare_to_send_from_internal_bres_user(context):
    """ set the from to the repondent as set in the helper"""
    step_impl_the_user_is_internal(context)
    step_impl_the_msg_from_is_set_to_internal_bres_user(context)
    step_impl_the_msg_to_is_set_to_respondent(context)


@given("the user token is set to respondent with no user id")
@when("the user token is set to respondent with no user id")
def step_impl_set_token_to_respondent_directly(context):
    """set the user token to be a respondent but have no user id"""
    with context.app.app_context():
        context.bdd_helper.token_data = {constants.USER_IDENTIFIER: "", "role": "respondent"}


@given("the user token is set to internal with no user id")
@when("the user token is set to internal with no user id")
def step_impl_set_token_to_internal_directly(context):
    """set the user token to an internal user withno user id"""
    with context.app.app_context():
        context.bdd_helper.token_data = {constants.USER_IDENTIFIER: "", "role": "internal"}


@given("the user token is set to a respondent with no role associated")
@when("the user token is set to a respondent with no role associated")
def step_impl_set_token_to_respondent_with_no_role(context):
    with context.app.app_context():
        context.bdd_helper.token_data = {constants.USER_IDENTIFIER: context.bdd_helper.respondent_id, "role": ""}


@given("the user token is set to a internal user with no role associated")
@when("the user token is set to a internal user with no role associated")
def step_impl_set_token_to_internal_with_no_role(context):
    with context.app.app_context():
        context.bdd_helper.token_data = {constants.USER_IDENTIFIER: context.bdd_helper.internal_id_bres_user, "role": ""}


# Version 2 Steps Below

@given("sending from respondent to internal specific user")
@when("sending from respondent to internal specific user")
def step_impl_prepare_to_send_from_respondent_to_non_bres_specific_user(context):
    """set the message to to the internal user as defined in the helper"""
    step_impl_the_user_is_set_as_respondent(context)
    step_impl_the_msg_from_is_set_to_respondent(context)
    step_impl_the_msg_to_is_set_to_internal_specific_user(context)


@given("sending from respondent to internal group")
@when("sending from respondent to internal group")
def step_impl_prepare_to_send_from_respondent_to_non_bres_group(context):
    """set the message to to the internal user as defined in the helper"""
    step_impl_the_user_is_set_as_respondent(context)
    step_impl_the_msg_from_is_set_to_respondent(context)
    step_impl_the_msg_to_is_set_to_internal_group_user(context)


@given("the user is set as internal specific user")
@when("the user is set as internal specific user")
def step_impl_the_user_is_internal_specific_user(context):
    """Set the user to the internal user"""
    with context.app.app_context():
        context.bdd_helper.token_data = context.bdd_helper.internal_specific_user_token


@given("the user is set to alternative internal specific user")
@when("the user is set to alternative internal specific user")
def step_impl_the_user_is_set_to_alternative_internal_specific_user(context):
    "Set the user to the alternative internal user"
    with context.app.app_context():
        context.bdd_helper.token_data = context.bdd_helper.alternative_internal_specific_user_token


@given("the user is set as internal group")
@when("the user is set as internal group")
def step_impl_the_user_is_internal_group_user(context):
    """Set the user to the internal user"""
    with context.app.app_context():
        context.bdd_helper.token_data = context.bdd_helper.internal_group_user_token


@given("sending from internal specific user to respondent")
@when("sending from internal specific user to respondent")
def step_impl_prepare_to_send_from_internal_specific_user_to_respondent(context):
    """set the message from to the internal user as defined in the helper"""
    step_impl_the_user_is_internal_specific_user(context)
    step_impl_the_msg_from_is_set_to_internal_specific_user(context)
    step_impl_the_msg_to_is_set_to_respondent(context)


@given("sending from internal group to respondent")
@when("sending from internal group to respondent")
def step_impl_prepare_to_send_from_rinternal_group_to_respondent(context):
    """set the message from to the internal user as defined in the helper"""
    step_impl_the_user_is_internal_group_user(context)
    step_impl_the_msg_from_is_set_to_internal_group_user(context)
    step_impl_the_msg_to_is_set_to_respondent(context)
