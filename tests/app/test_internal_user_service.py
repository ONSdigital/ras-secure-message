import unittest

import requests_mock
from flask import current_app
from requests import HTTPError

from secure_message import constants
from secure_message.application import create_app
from secure_message.services.internal_user_service import InternalUserService


class PartyBusinessTestHelper:
    def __init__(self, status_code, reason, text):
        self.status_code = status_code
        self.reason = reason
        self.text = text


class InternalUserServiceTestCase(unittest.TestCase):
    """Test cases for internal user service"""

    def setUp(self):
        """creates a test client"""
        self.app = create_app(config="TestConfig")
        self.app.oauth_client_token = {
            "access_token": "705288eea2474641bde364032d465157",
            "token_type": "bearer",
            "expires_in": 43199,
            "scope": "clients.read emails.write scim.userids password.write idps.write notifications.write "
            "oauth.login scim.write critical_notifications.write",
            "jti": "705288eea2474641bde364032d465157",
        }

    def test_results_default_information_returned_for_group_user(self):
        """Test get business details sends a request and returns data"""

        sut = InternalUserService()
        expected = {
            "id": constants.NON_SPECIFIC_INTERNAL_USER,
            "firstName": "ONS",
            "lastName": "User",
            "emailAddress": "",
        }
        actual = sut.get_user_details(constants.NON_SPECIFIC_INTERNAL_USER)

        self.assertEqual(expected, actual)

    @requests_mock.mock()
    def test_default_user_returned_if_http_error_403(self, mock_request):
        NON_CURRENT_USER = "bb7c51c0-96b7-441d-9881-4ad1a3d3d396"
        with self.app.app_context():
            with current_app.test_request_context():
                uaa_url = f"{current_app.config['UAA_URL']}/Users/{NON_CURRENT_USER}"
                mock_request.get(uaa_url, status_code=403, reason="Forbidden", text="{}")
                with self.assertRaises(HTTPError):
                    InternalUserService().get_user_details(NON_CURRENT_USER)

    @requests_mock.mock()
    def test_default_user_returned_if_http_error_404(self, mock_request):
        NON_CURRENT_USER = "bb7c51c0-96b7-441d-9881-4ad1a3d3d396"
        with self.app.app_context():
            with current_app.test_request_context():
                uaa_url = f"{current_app.config['UAA_URL']}/Users/{NON_CURRENT_USER}"
                mock_request.get(uaa_url, status_code=404, reason="Not found", text="{}")
                response = InternalUserService().get_user_details(NON_CURRENT_USER)
                self.assertEqual(NON_CURRENT_USER, response["id"])


if __name__ == "__main__":
    unittest.main()
