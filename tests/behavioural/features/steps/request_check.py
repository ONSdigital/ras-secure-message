from behave import given, when
from app.application import app
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings

token_data = {
            "user_urn": "000000000"
        }

headers = {'Content-Type': 'application/json', 'authentication': ''}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['authentication'] = update_encrypted_jwt()


# Scenario: Retrieve a message with correct missing ID


@given("no user urn is in the header")
def step_impl(context):
    if 'user_urn' in token_data:
        del token_data['user_urn']
        headers['authentication'] = update_encrypted_jwt()


@when("a GET request is made")
def step_impl(context):
    url = "http://localhost:5050/message/1"
    context.response = app.test_client().get(url, headers=headers)


# Scenario: Retrieve a message with incorrect missing ID


@when("a POST request is made")
def step_impl(context):
    url = "http://localhost:5050/message/send"
    context.response = app.test_client().post(url, headers=headers)
