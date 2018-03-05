import unittest

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
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True

    def test_results_default_information_returned_for_bres_user(self):
        """Test get business details sends a request and returns data"""

        sut = InternalUserService()
        expected = {"id": constants.BRES_USER,
                    "firstName": "BRES",
                    "lastName": "",
                    "emailAddress": ""
                    }
        actual = sut.get_user_details(constants.BRES_USER)

        self.assertEqual(expected, actual)

    def test_results_default_information_returned_for_group_user(self):
        """Test get business details sends a request and returns data"""

        sut = InternalUserService()
        expected = {"id": constants.NON_SPECIFIC_INTERNAL_USER,
                    "firstName": "ONS",
                    "lastName": "User",
                    "emailAddress": "N/A"
                    }
        actual = sut.get_user_details(constants.NON_SPECIFIC_INTERNAL_USER)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
