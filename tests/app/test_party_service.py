import unittest

from flask import current_app
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
    def test_results_returned_from_get_business_details_returned_as_expected(self, mock_request):
        """Test get business details sends a request and returns data"""
        ru = "1234"
        business_data_url = self.app.config['RAS_PARTY_GET_BY_BUSINESS'].format(self.app.config['RAS_PARTY_SERVICE'], ru)
        mock_request.get(business_data_url, status_code=200, reason="OK", text='{"something": "else"}')
        sut = PartyService()

        with self.app.app_context():
            result_data, result_status = sut.get_business_details(ru)

        self.assertEqual(result_data, {"something": "else"})
        self.assertEqual(result_status, 200)

    @requests_mock.mock()
    def test_get_business_details_converts_error_list_to_errors_dictionary(self,  mock_request):
        """Test get business details and returns correctly from a list"""
        ru = "1234"
        business_data_url = self.app.config['RAS_PARTY_GET_BY_BUSINESS'].format(self.app.config['RAS_PARTY_SERVICE'], ru)
        sut = PartyService()
        mock_request.get(business_data_url, status_code=200, reason="OK", text='[{"errors": "test"}]')

        with self.app.app_context():
            result_data, result_status = sut.get_business_details(ru)

        self.assertEqual(result_data, [{"errors": "test"}])
        self.assertEqual(result_status, 200)

    @requests_mock.mock()
    def test_get_business_details_fails(self, mock_request):
        """Test get business details and returns correctly from a list"""
        ru = "1234"
        business_data_url = self.app.config['RAS_PARTY_GET_BY_BUSINESS'].format(self.app.config['RAS_PARTY_SERVICE'], ru)
        sut = PartyService()
        mock_request.get(business_data_url, status_code=401, reason="unauthorised", text='Unauthorized Access')

        with self.app.app_context():
            result_data, result_status = sut.get_business_details(ru)

        self.assertEqual(result_data, "Unauthorized Access")
        self.assertEqual(result_status, 401)

    @requests_mock.mock()
    def test_get_user_details_for_bres_user(self, mock_request):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        user_data_url = self.app.config['RAS_PARTY_GET_BY_RESPONDENT'].format(self.app.config['RAS_PARTY_SERVICE'],
                                                                                   constants.BRES_USER)

        expected_result = {'emailAddress': '',
                           'firstName': constants.BRES_USER,
                           'id': constants.BRES_USER,
                           'lastName': '',
                           'sampleUnitType': 'BI',
                           'status': '',
                           'telephone': ''}

        mock_request.get(user_data_url, status_code=200, reason="OK", text="{}".format(expected_result))

        with self.app.app_context():
            result_data, result_status = sut.get_user_details(constants.BRES_USER)

        self.assertEqual(result_data, expected_result)
        self.assertEqual(result_status, 200)

    @requests_mock.mock()
    def test_get_user_details_calls_party_service_for_respondent(self, mock_request):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        user_data_url = self.app.config['RAS_PARTY_GET_BY_RESPONDENT'].format(self.app.config['RAS_PARTY_SERVICE'], 'NotBres')
        mock_request.get(user_data_url, status_code=200, reason="OK", text='{"Test": "test"}')

        with self.app.app_context():
            result_data, result_status = sut.get_user_details('NotBres')

        self.assertEqual(result_data, {"Test": "test"})
        self.assertEqual(result_status, 200)

    @requests_mock.mock()
    def test_get_user_details_calls_party_service_for_respondent_unauthorised(self, mock_request):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        user_data_url = self.app.config['RAS_PARTY_GET_BY_RESPONDENT'].format(self.app.config['RAS_PARTY_SERVICE'], 'NotBres')
        mock_request.get(user_data_url, status_code=401, reason="unauthorised", text="Unauthorized access")

        with self.app.app_context():
            result_data, result_status = sut.get_user_details('NotBres')

        self.assertEqual(result_data, "Unauthorized access")
        self.assertEqual(result_status, 401)


if __name__ == '__main__':
    unittest.main()
