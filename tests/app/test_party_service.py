import unittest
from unittest import mock
from app.services.party_service import PartyService
import requests
import json
import app.settings
from app import constants


class PartyBusinessTestHelper:
    def __init__(self, status_code, reason, text):
        self.status_code = status_code
        self.reason = reason
        self.text = text


class PartyTestCase(unittest.TestCase):
    """Test cases for party service"""

    @staticmethod
    def test_get_business_details_sends_request_to_remote_party_service():
        """Test get business details sends a request"""
        sut = PartyService()
        business_data = PartyBusinessTestHelper(200, "OK", '{"something": "else"}')
        requests.get = mock.Mock(name='get', return_value=business_data)

        ru = '1234'
        url = app.settings.RAS_PARTY_GET_BY_BUSINESS.format(app.settings.RAS_PARTY_SERVICE, ru)
        
        sut.get_business_details(ru)

        requests.get.assert_called_with(url, verify=False)

    def test_results_returned_from_get_business_details_returned_as_expected(self):
        """Test get business details sends a request and returns data"""
        sut = PartyService()
        business_data = PartyBusinessTestHelper(200, "OK", '{"something": "else"}')
        requests.get = mock.Mock(name='get', return_value=business_data)

        result_data, result_status = sut.get_business_details('1234')

        self.assertEqual(result_data, json.loads(business_data.text))
        self.assertEqual(result_status, 200)

    def test_get_business_details_converts_error_list_to_errors_dictionary(self):
        """Test get business details and returns correctly from a list"""
        sut = PartyService()
        business_data = PartyBusinessTestHelper(200, "OK", '[{"errors": "test"}]')
        requests.get = mock.Mock(name='get', return_value=business_data)

        result_data, result_status = sut.get_business_details("1234")

        self.assertEqual(result_data, {'errors': {'errors': 'test'}})
        self.assertEqual(result_status, 200)

    def test_get_user_details_for_bres_user(self):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        business_data = PartyBusinessTestHelper(200, "OK", '{"something": "else"}')
        requests.get = mock.Mock(name='get', return_value=business_data)

        expected_result = {'emailAddress': '',
                           'firstName': constants.BRES_USER,
                           'id': constants.BRES_USER,
                           'lastName': '',
                           'sampleUnitType': 'BI',
                           'status': '',
                           'telephone': ''}

        result_data, result_status = sut.get_user_details(constants.BRES_USER)

        self.assertEqual(result_data, expected_result)
        self.assertEqual(result_status, 200)

    def test_get_user_details_calls_party_service_for_respondent(self):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        expected = PartyBusinessTestHelper(200, "OK", '{"Test": "test"}')
        requests.get = mock.Mock(name='get', return_value=expected)

        result_data, result_status = sut.get_user_details('Not Bres')

        self.assertEqual(result_data, json.loads(expected.text))
        self.assertEqual(result_status, 200)
