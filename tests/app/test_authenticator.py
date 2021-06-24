import unittest

from flask import Response
from werkzeug.exceptions import BadRequest

from secure_message import constants
from secure_message.application import create_app
from secure_message.authentication.authenticator import authenticate, check_jwt
from secure_message.authentication.jwt import decode, encode


class AuthenticationTestCase(unittest.TestCase):
    """Test case for request authentication"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app(config='TestConfig')

    def test_authentication_jwt_pass(self):
        """Authenticate request using correct JWT"""
        expected_res = {'status': "ok"}
        data = {constants.USER_IDENTIFIER: "ce12b958-2a5f-44f4-a6da-861e59070a31",
                "role": "internal"}

        with self.app.app_context():
            jwt = encode(data)
            res = check_jwt(jwt)

        self.assertEqual(res, expected_res)

    def test_authentication_jwt_invalid_fail(self):
        """Authenticate request using incorrect JWT"""
        expected_res = Response(response="Invalid token to access this Microservice Resource",
                                status=400, mimetype="text/html")

        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
               'eyJSVSI6IjEyMzQ1Njc4OTEwIiwic3VydmV5IjoiQlJTIiwiQ0MiOiIxMiJ9.'
               'uKn_qlmXLsYd_k1hNt2QfLabypLOXjO1_9cEuArJ-hE')
        with self.app.app_context():
            res = check_jwt(jwt)
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_user_urn_missing_fail(self):
        """Authenticate request with missing user_urn claim"""

        data = {}

        with self.app.app_context():
            signed_jwt = encode(data)
            with self.assertRaises(BadRequest):
                check_jwt(signed_jwt)

    def test_authenticate_request_with_correct_header_data(self):
        """Authenticate request using authenticate function and with correct header data"""
        expected_res = {'status': "ok"}
        data = {constants.USER_IDENTIFIER: "12345678910",
                "role": "internal"}

        with self.app.app_context():
            signed_jwt = encode(data)
            res = authenticate(headers={'Authorization': signed_jwt})
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

    def test_authentication_non_encrypted_jwt_pass(self):
        """Authenticate request using an un-ecrypted JWT"""
        expected_res = {'status': "ok"}
        data = {
            constants.USER_IDENTIFIER: "ce12b958-2a5f-44f4-a6da-861e59070a31",
            "role": "internal"
        }

        with self.app.app_context():
            signed_jwt = encode(data)
            res = check_jwt(signed_jwt)
        self.assertEqual(res, expected_res)


if __name__ == '__main__':
    unittest.main()
