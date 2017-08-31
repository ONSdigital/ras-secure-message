import nose.tools
from behave import given, then, when
from flask import json
from app import constants
from app.services.service_toggles import party, case_service

@then("new retrieved message additional from data matches that from party service")
def step_impl_verify_additional_from_data_matches_that_from_party_service(context):
    msg_resp = json.loads(context.response.data)
    party_data, party_status = party.get_user_details(msg_resp['msg_from'])
    nose.tools.assert_equal(msg_resp['@msg_from'], party_data)


@then("new retrieved message additional to data matches that from party service")
def step_impl_verify_additional_to_data_matches_that_from_party_service(context):
    msg_resp = json.loads(context.response.data)
    party_data, party_status = party.get_user_details(msg_resp['msg_to'][0])
    nose.tools.assert_equal(msg_resp['@msg_to'][0], party_data)


@then("new retrieved message additional ru_id data matches that from party service")
def step_impl_verify_additional_to_data_matches_that_from_party_service(context):
    msg_resp = json.loads(context.response.data)
    party_data, party_status = party.get_business_details(msg_resp['ru_id'])
    nose.tools.assert_equal(msg_resp['@ru_id'], party_data)