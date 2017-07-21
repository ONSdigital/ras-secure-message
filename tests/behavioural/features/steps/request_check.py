from behave import given, when, then
from app.application import app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings
import nose.tools

token_data = {
            "user_uuid": "000000000",
            "role": "internal"
        }

headers = {'Content-Type': 'application/json', 'Authorization': ''}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)


headers['Authorization'] = update_encrypted_jwt()


# Scenario 1: GET request without a user urn in header (see common steps)
# Scenario 2: POST request without user in header (see common steps)
# Scenario 3: PUT request without a user in header (see common steps)
# Scenario 4: GET request without a role in header (see common steps)
# Scenario 5: POST request without a role in header (see common steps)
# Scenario 6: PUT request without a role in header (see common steps)
# Scenario 7: User tries to use endpoint with the wrong method
@given("user wants to use /draft/save endpoint")
def step_impl_use_draft_save_endpoint(context):
    context.url = "http://localhost:5050/draft/save"


@given("user wants to use /health endpoint")
def step_impl_use_health_endpoint(context):
    context.url = "http://localhost:5050/health"


@given("user wants to use /health/db endpoint")
def step_impl_use_health_db_endpoint(context):
    context.url = "http://localhost:5050/health/db"


@given("user wants to use /health/details endpoint")
def step_impl_use_health_details_endpoint(context):
    context.url = "http://localhost:5050/health/details"


@given("user wants to use /message/id endpoint")
def step_impl_use_message_id_endpoint(context):
    context.url = "http://localhost:5050/message/1"


@given("user wants to use /message/id/modify endpoint")
def step_impl_use_message_id_modify_endpoint(context):
    context.url = "http://localhost:5050/message/1/modify"


@given("user wants to use /message/send endpoint")
def step_impl_use_message_send_endpoint(context):
    context.url = "http://localhost:5050/message/send"


@given("user wants to use /messages endpoint")
def step_impl_use_messages_endpoint(context):
    context.url = "http://localhost:5050/messages"


@when("user tries to access that endpoint with the POST method")
def step_impl_access_endpoint_withpost(context):
    token_data.update({
        "user_urn": "000000000"
    })
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().post(context.url, headers=headers)


@when("user tries to access that endpoint with the GET method")
def step_impl_access_endpoint_with_get(context):
    token_data.update({
        "user_urn": "000000000"
    })
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().get(context.url, headers=headers)


@when("user tries to access that endpoint with the PUT method")
def step_impl_access_endpoint_with_put(context):
    token_data.update({
        "user_urn": "000000000"
    })
    headers['Authorization'] = update_encrypted_jwt()
    context.response = app.test_client().put(context.url, headers=headers)


@then("a 405 error status is returned")
def step_impl_assert_405_returned(context):
    nose.tools.assert_equal(context.response.status_code, 405)


# Common Steps: used in multiple scenarios
@given("no user uuid is in the header")
def step_impl_no_user_urn_in_the_header(context):
    if 'user_uuid' in token_data:
        del token_data['user_uuid']
        headers['Authorization'] = update_encrypted_jwt()


@given("no role is in the header")
def step_impl_no_role_in_the_header(context):
    if 'user_uuid' not in token_data:
        token_data['user_uuid'] = "000000000"

    if 'role' in token_data:
        del token_data['role']
        headers['Authorization'] = update_encrypted_jwt()


@when("a POST request is made")
def step_impl_post_request_is_made(context):
    url = "http://localhost:5050/message/send"
    context.response = app.test_client().post(url, headers=headers)


@when("a PUT request is made")
def step_impl_put_request_is_made(context):
    url = "http://localhost:5050/message/1/modify"
    context.response = app.test_client().put(url, headers=headers)


@when("a GET request is made")
def step_impl_get_request_is_made(context):
    url = "http://localhost:5050/message/1"
    context.response = app.test_client().get(url, headers=headers)
