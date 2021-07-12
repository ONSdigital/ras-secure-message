import unittest

from secure_message import constants
from secure_message.services.internal_user_service import InternalUserService


class PartyBusinessTestHelper:
    def __init__(self, status_code, reason, text):
        self.status_code = status_code
        self.reason = reason
        self.text = text


class InternalUserServiceTestCase(unittest.TestCase):
    """Test cases for internal user service"""

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


if __name__ == "__main__":
    unittest.main()
