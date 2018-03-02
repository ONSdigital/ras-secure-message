import unittest

import requests_mock
from secure_message import constants
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

    @requests_mock.mock()
    def test_results_returned_from_get_business_get_executed_just_once_for_the_same_ru(self, mock_request):
        """Test get business details sends a request and returns data"""
        ru = "1234"
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses/id/{ru}"
        mock_request.get(business_data_url, status_code=200, reason="OK", text='{"something": "else"}')
        sut = PartyService()

        for retries in range(0, 2):

            with self.app.app_context():
                sut.get_business_details(ru)

        self.assertTrue(mock_request.call_count == 1)

    @requests_mock.mock()
    def test_results_returned_from_get_business_get_executed_twice_for_different_ru(self, mock_request):
        """Test get business details sends a request and returns data"""
        ru = "1234"

        sut = PartyService()
        count = 0
        for retries in range(0, 2):
            count += 1
            ru += str(count)
            business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses/id/{ru}"
            mock_request.get(business_data_url, status_code=200, reason="OK", text='{"something": "else"}')

            with self.app.app_context():
                sut.get_business_details(ru)

        self.assertTrue(mock_request.call_count == 2)

    @requests_mock.mock()
    def test_results_returned_from_get_business_details_returned_as_expected(self, mock_request):
        """Test get business details sends a request and returns data"""
        ru = "1234"
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses/id/{ru}"
        mock_request.get(business_data_url, status_code=200, reason="OK", text='{"something": "else"}')
        sut = PartyService()

        with self.app.app_context():
            result_data = sut.get_business_details(ru)

        self.assertEqual(result_data, {"something": "else"})

    @requests_mock.mock()
    def test_get_business_details_converts_error_list_to_errors_dictionary(self, mock_request):
        """Test get business details and returns correctly from a list"""
        ru = "1234"
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses/id/{ru}"
        sut = PartyService()
        mock_request.get(business_data_url, status_code=200, reason="OK", text='[{"errors": "test"}]')

        with self.app.app_context():
            result_data = sut.get_business_details(ru)

        self.assertEqual(result_data, [{"errors": "test"}])

    @requests_mock.mock()
    def test_get_business_details_fails_business_data_is_none(self, mock_request):
        """Test get business details and returns correctly from a list"""
        ru = "1234"
        business_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses/id/{ru}"
        sut = PartyService()
        mock_request.get(business_data_url, status_code=401, reason="unauthorised", text='Unauthorized Access')

        with self.app.app_context():
            result_data = sut.get_business_details(ru)

        self.assertIsNone(result_data)

    @requests_mock.mock()
    def test_get_user_details_for_bres_user(self, mock_request):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents/id/{constants.BRES_USER}"
        expected_result = {'emailAddress': '',
                           'firstName': constants.BRES_USER,
                           'id': constants.BRES_USER,
                           'lastName': '',
                           'sampleUnitType': 'BI',
                           'status': '',
                           'telephone': ''}

        mock_request.get(user_data_url, status_code=200, reason="OK", text=str(expected_result))

        with self.app.app_context():
            result_data = sut.get_user_details(constants.BRES_USER)

        self.assertEqual(result_data, expected_result)

    @requests_mock.mock()
    def test_get_user_details_calls_party_service_for_respondent(self, mock_request):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents/id/NotBres"
        mock_request.get(user_data_url, status_code=200, reason="OK", text='{"Test": "test"}')

        with self.app.app_context():
            result_data = sut.get_user_details('NotBres')

        self.assertEqual(result_data, {"Test": "test"})

    @requests_mock.mock()
    def test_get_user_details_is_none_for_unauthorised_party_service_access(self, mock_request):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        user_data_url = f"{self.app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents/id/NotBres"
        mock_request.get(user_data_url, status_code=401, reason="unauthorised", text="Unauthorized access")

        with self.app.app_context():
            result_data = sut.get_user_details('NotBres')

        self.assertIsNone(result_data)


if __name__ == '__main__':
    unittest.main()
