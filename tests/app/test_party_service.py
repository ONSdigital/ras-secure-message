import unittest
from unittest import mock
from app.services.party_service import PartyService
import requests
import json


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

        result_data, result_status = sut.get_business_details('1234')

        requests.get.assert_called_with('http://localhost:8001/party-api/v1/businesses/id/1234', verify=False)

    def test_send_request_to_remote_party_service_and_return_details(self):
        """Test get business details sends a request and returns data"""
        sut = PartyService()
        business_data = PartyBusinessTestHelper(200, "OK", '{"something": "else"}')
        requests.get = mock.Mock(name='get', return_value=business_data)

        result_data, result_status = sut.get_business_details('1234')

        self.assertEqual(result_data, json.loads(business_data.text))
        self.assertEqual(result_status, 200)

    # def test_get_business_details_converts_error_list_to_errors_dictionary(self):
    #     """Test get business details and returns correctly from a list"""
    #     sut = PartyService()
    #     business_data = PartyBusinessTestHelper(200, "OK", '{"something": "else"}')
    #     requests.get = mock.Mock(name='get', return_value=business_data)
    #
    #     result_data, result_status = sut.get_business_details("1234")
    #
    #     self.assertEqual(result_data, "['something', 'else]")
    #     self.assertEqual(result_status, 200)
    #     pass

    def test_get_user_details_for_bres_user(self):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        business_data = PartyBusinessTestHelper(200, "OK", '{"something": "else"}')
        requests.get = mock.Mock(name='get', return_value=business_data)

        result_data, result_status = sut.get_user_details('BRES')

        expected_result = {'emailAddress': '',
                           'firstName': 'BRES',
                           'id': 'BRES',
                           'lastName': '',
                           'sampleUnitType': 'BI',
                           'status': '',
                           'telephone': ''}

        self.assertEqual(result_data, expected_result)
        self.assertEqual(result_status, 200)

    def test_get_user_details_calls_party_service_for_respondent(self):
        """Test get user details sends a request and receives back data"""
        sut = PartyService()
        business_data = PartyBusinessTestHelper(200, "OK", '{"Test": "test"}')
        requests.get = mock.Mock(name='get', return_value=business_data)

        result_data, result_status = sut.get_user_details('Not Bres')

        self.assertEqual(result_data, json.loads(business_data.text))
        self.assertEqual(result_status, 200)
