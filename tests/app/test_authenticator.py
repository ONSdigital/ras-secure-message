import unittest

from flask import Response
from werkzeug.exceptions import BadRequest

from secure_message.application import create_app
from secure_message.authentication.authenticator import check_jwt, authenticate
from secure_message.authentication.jwt import encode, decode
from secure_message.authentication.jwe import Encrypter
from secure_message import constants


def test_authentication_non_encrypted_jwt_pass(self):
    """Authenticate request using an un-ecrypted JWT"""
    expected_res = {'status': "ok"}
    data = {
        constants.USER_IDENTIFIER: "ce12b958-2a5f-44f4-a6da-861e59070a31",
        "role": "internal"
    }

    signed_jwt = encode(data)
    app = create_app()
    with app.app_context():
        app.config['SM_JWT_ENCRYPT'] = 0
        res = check_jwt(signed_jwt)
    self.assertEqual(res, expected_res)


class AuthenticationTestCase(unittest.TestCase):
    """Test case for request authentication"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()

    def test_authentication_jwt_pass(self):
        """Authenticate request using correct JWT"""
        expected_res = {'status': "ok"}
        data = {constants.USER_IDENTIFIER: "ce12b958-2a5f-44f4-a6da-861e59070a31",
                "role": "internal"}

        encrypter = Encrypter(_private_key=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY'],
                              _private_key_password=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD'],
                              _public_key=self.app.config['SM_USER_AUTHENTICATION_PUBLIC_KEY'])
        with self.app.app_context():
            signed_jwt = encode(data)
            encrypted_jwt = encrypter.encrypt_token(signed_jwt)
            res = check_jwt(encrypted_jwt)
        self.assertEqual(res, expected_res)

    def test_authentication_jwt_invalid_fail(self):
        """Authenticate request using incorrect JWT"""
        expected_res = Response(response="Invalid token to access this Microservice Resource",
                                status=400, mimetype="text/html")

        encrypter = Encrypter(_private_key=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY'],
                              _private_key_password=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD'],
                              _public_key=self.app.config['SM_USER_AUTHENTICATION_PUBLIC_KEY'])

        encrypted_jwt = encrypter.encrypt_token('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                                                'eyJSVSI6IjEyMzQ1Njc4OTEwIiwic3VydmV5IjoiQlJTIiwiQ0MiOiIxMiJ9.'
                                                'uKn_qlmXLsYd_k1hNt2QfLabypLOXjO1_9cEuArJ-hE')
        with self.app.app_context():
            res = check_jwt(encrypted_jwt)
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_user_urn_missing_fail(self):
        """Authenticate request with missing user_urn claim"""

        data = {}

        encrypter = Encrypter(_private_key=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY'],
                              _private_key_password=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD'],
                              _public_key=self.app.config['SM_USER_AUTHENTICATION_PUBLIC_KEY'])
        with self.app.app_context():
            signed_jwt = encode(data)
            encrypted_jwt = encrypter.encrypt_token(signed_jwt)
            with self.assertRaises(BadRequest):
                check_jwt(encrypted_jwt)

    def test_authentication_jwt_not_encrypted_fail(self):
        """Authenticate request using JWT without encryption"""

        data = {constants.USER_IDENTIFIER: "12345678910"}

        with self.app.app_context():
            with self.assertRaises(BadRequest):
                check_jwt(encode(data))

    def test_authenticate_request_with_correct_header_data(self):
        """Authenticate request using authenticate function and with correct header data"""
        expected_res = {'status': "ok"}
        data = {constants.USER_IDENTIFIER: "12345678910",
                "role": "internal"}

        encrypter = Encrypter(_private_key=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY'],
                              _private_key_password=self.app.config['SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD'],
                              _public_key=self.app.config['SM_USER_AUTHENTICATION_PUBLIC_KEY'])

        with self.app.app_context():
            signed_jwt = encode(data)
            encrypted_jwt = encrypter.encrypt_token(signed_jwt)
            res = authenticate(headers={'Authorization': encrypted_jwt})
        self.assertEqual(res, expected_res)

    def test_authenticate_request_with_incorrect_header_data(self):
        """Authenticate request using authenticate function and without header data"""
        expected_res = Response(response="Invalid token to access this Microservice Resource",
                                status=400, mimetype="text/html")
        with self.app.app_context():
            res = authenticate(headers={})
        self.assertEqual(res._status, expected_res._status)

    def test_encode_decode_jwt(self):
        """decoding and encoding jwt"""
        data = {constants.USER_IDENTIFIER: "12345678910"}

        with self.app.app_context():
            signed_jwt = encode(data)
            decoded_jwt = decode(signed_jwt)
        self.assertEqual(data, decoded_jwt)


if __name__ == '__main__':
    unittest.main()
