from app.authentication.authenticator import check_jwt
from app.authentication.jwt import encode
from flask import Response
import unittest


class AuthenticationTestCase(unittest.TestCase):
    """Test case for request authentication"""
    def test_authentication_jwt_pass(self):
        """Authenticate request using correct JWT"""
        expected_res = {'status': "ok"}
        data = {
                  "RU": "12345678910",
                  "survey": "BRS",
                  "CC": "URN"
                }
        res = check_jwt(encode(data))
        self.assertEqual(res, expected_res)

    def test_authentication_jwt_invalid_fail(self):
        """Authenticate request using incorrect JWT"""
        expected_res = Response(response="Invalid token to access this Microservice Resource",
                                status=400, mimetype="text/html")
        res = check_jwt('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                        'eyJSVSI6IjEyMzQ1Njc4OTEwIiwic3VydmV5IjoiQlJTIiwiQ0MiOiIxMiJ9.'
                        'uKn_qlmXLsYd_k1hNt2QfLabypLOXjO1_9cEuArJ-hE')
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_ru_invalid_fail(self):
        """Authenticate request using invalid RU claim"""
        expected_res = Response(response="Missing RU or invalid RU supplied to access this Microservice Resource",
                                status=400, mimetype="text/html")
        data = {
            "RU": "123456789",
            "survey": "BRS",
            "CC": "URN"
        }
        res = check_jwt(encode(data))
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_ru_missing_fail(self):
        """Authenticate request with missing RU claim"""
        expected_res = Response(response="Missing RU or invalid RU supplied to access this Microservice Resource",
                                status=400, mimetype="text/html")
        data = {
            "survey": "BRS",
            "CC": "URN"
        }

        res = check_jwt(encode(data))
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_survey_invalid_fail(self):
        """Authenticate request using invalid survey claim"""
        expected_res = Response(response="Survey required to access this Microservice Resource",
                                status=400, mimetype="text/html")
        data = {
            "RU": "12345678910",
            "survey": "",
            "CC": "URN"
        }
        res = check_jwt(encode(data))
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_survey_missing_fail(self):
        """Authenticate request with missing survey claim"""
        expected_res = Response(response="Survey required to access this Microservice Resource",
                                status=400, mimetype="text/html")
        data = {
            "RU": "12345678910",
            "CC": "URN"
        }

        res = check_jwt(encode(data))
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_cc_invalid_fail(self):
        """Authenticate request using invalid CC claim"""
        expected_res = Response(response="Collection Case required to access this Microservice Resource",
                                status=400, mimetype="text/html")
        data = {
            "RU": "12345678910",
            "survey": "BRS",
            "CC": ""
        }
        res = check_jwt(encode(data))
        self.assertEqual(res.response, expected_res.response)

    def test_authentication_jwt_cc_missing_fail(self):
        """Authenticate request with missing CC claim"""
        expected_res = Response(response="Collection Case required to access this Microservice Resource",
                                status=400, mimetype="text/html")
        data = {
            "RU": "12345678910",
            "survey": "BRS"
        }

        res = check_jwt(encode(data))
        self.assertEqual(res.response, expected_res.response)
