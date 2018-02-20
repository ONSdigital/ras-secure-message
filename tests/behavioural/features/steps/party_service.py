from behave import given, when
from unittest.mock import patch

from secure_message.api_mocks.party_service_mock import PartyServiceMock


@given("party service forgets alternative respondent")
@when("party service forgets alternative respondent")
def step_impl_party_service_forgets_alternative_respondent(context):
    """set the message data ru to a specific value"""
    cp = PartyServiceMock._respondent_ids.copy()
    del cp[context.bdd_helper.alternative_respondent_id]
    patch.dict(PartyServiceMock._respondent_ids, cp)

