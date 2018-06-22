import unittest

import requests_mock
from secure_message.application import create_app
from secure_message.services.party_service import PartyService


class PartyBusinessTestHelper:
    def __init__(self, status_code, reason, text):
        self.status_code = status_code
        self.reason = reason
        self.text = text


class PartyTestCase(unittest.TestCase):
    """Test cases for party service"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True

    # Get business details tests
    @requests_mock.mock()
    def test_get_business_details_single_id_success(self, mock_request):
        """Test get business details with a single uuid"""
        ru_ids = ["b08c07c3-df28-4283-bb4c-c048729ce372"]
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses?id={ru_ids[0]}"
        mock_request.get(business_data_url, status_code=200, reason="OK", text='{}')

        with self.app.app_context():
            PartyService().get_business_details(ru_ids)

        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_business_details_multiple_id_success(self, mock_request):
        """Test get business details with a multiple uuids at once"""
        ru_ids = ["c614e64e-d981-4eba-b016-d9822f09a4fb", "c614e64e-d981-4eba-b016-d9822f09a4f2"]
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses?id={ru_ids[0]}&id={ru_ids[1]}"
        mock_request.get(business_data_url, status_code=200, reason="OK", text='{}')
        with self.app.app_context():
            PartyService().get_business_details(ru_ids)

        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_business_details_client_error(self, mock_request):
        """Test get business details fails and returns an empty list when a non-uuid is sent"""
        ru_ids = ["not_a_uuid"]
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses?id={ru_ids[0]}"
        mock_request.get(business_data_url, status_code=400, reason="Invalid uuid", text='{"error": "text"}')
        with self.app.app_context():
            result = PartyService().get_business_details(ru_ids)

        self.assertEqual(result, [])
        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_business_details_unauthorised_failure(self, mock_request):
        """Test get business details fails and returns and empty list when the client is unauthorised to access the party service"""
        ru_ids = ["1234"]
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses?id={ru_ids[0]}"
        mock_request.get(business_data_url, status_code=401, reason="unauthorised", text='{}')
        with self.app.app_context():
            result_data = PartyService().get_business_details(ru_ids)

        self.assertEqual(result_data, [])
        self.assertTrue(mock_request.call_count == 1)

    # Get user (singular) details tests
    @requests_mock.mock()
    def test_get_user_details_success(self, mock_request):
        """Test get user details with a single uuid"""
        user_id = "c614e64e-d981-4eba-b016-d9822f09a4fb"
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents?id={user_id}"
        mock_request.get(user_data_url, status_code=200, reason="OK", text='{}')
        with self.app.app_context():
            PartyService().get_user_details(user_id)

        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_user_details_client_error(self, mock_request):
        """Test get user details fails and returns an empty list when a non-uuid is sent"""
        user_id = "not_a_uuid"
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents?id={user_id}"
        mock_request.get(user_data_url, status_code=400, reason="Invalid uuid", text='{}')
        with self.app.app_context():
            result = PartyService().get_user_details(user_id)

        self.assertEqual(result, [])
        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_user_details_unauthorised_failure(self, mock_request):
        """Test get user details fails and returns and empty list when the client is unauthorised to access the party service"""
        user_ids = ['NotBres']
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents?id={user_ids[0]}"
        mock_request.get(user_data_url, status_code=401, reason="unauthorised", text='{}')

        with self.app.app_context():
            result_data = PartyService().get_users_details(user_ids)

        self.assertEqual(result_data, [])
        self.assertTrue(mock_request.call_count == 1)

    # Get users (plural) details tests
    @requests_mock.mock()
    def test_get_users_details_single_id_success(self, mock_request):
        """Test get users details sends a request and receives back data"""
        user_ids = ["c614e64e-d981-4eba-b016-d9822f09a4fb"]
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents?id={user_ids[0]}"
        mock_request.get(user_data_url, status_code=200, reason="OK", text='{}')

        with self.app.app_context():
            PartyService().get_users_details(user_ids)

        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_users_details_multiple_id_success(self, mock_request):
        """Test get users details with a multiple uuids at once"""
        user_ids = ["c614e64e-d981-4eba-b016-d9822f09a4fb", "c614e64e-d981-4eba-b016-d9822f09a4f2"]
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents?id={user_ids[0]}&id={user_ids[1]}"
        mock_request.get(user_data_url, status_code=200, reason="OK", text='{}')
        with self.app.app_context():
            PartyService().get_users_details(user_ids)

        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_users_details_client_error(self, mock_request):
        """Test get users details fails and returns an empty list when a non-uuid is sent"""
        user_ids = ["not_a_uuid"]
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents?id={user_ids[0]}"
        mock_request.get(user_data_url, status_code=400, reason="Invalid uuid", text='{}')
        with self.app.app_context():
            result = PartyService().get_users_details(user_ids)

        self.assertEqual(result, [])
        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_get_users_details_unauthorised_failure(self, mock_request):
        """Test get users details fails and returns and empty list when the client is unauthorised to access the party service"""
        user_ids = ['1234', '4567']
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents?id={user_ids[0]}&id={user_ids[1]}"
        mock_request.get(user_data_url, status_code=401, reason="unauthorised", text='{}')

        with self.app.app_context():
            result_data = PartyService().get_users_details(user_ids)

        self.assertEqual(result_data, [])
        self.assertTrue(mock_request.call_count == 1)


if __name__ == '__main__':
    unittest.main()
