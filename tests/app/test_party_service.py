import unittest
from unittest import mock
from app.services.party_service import PartyService
import requests


class PartyBusinessTestHelper:

    def __init__(self, status_code, reason, text):
        self.status_code = status_code
        self.reason= reason
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

        assert requests.get.called

    def test_get_business_details_converts_error_list_to_errors_dictionary(self):
        pass

    def test_get_user_details_returns_constant_for_bres_user(self):
        pass

    def test_get_user_details_does_not_call_party_service_for_bres_user(self):
        pass

    def test_get_user_details_calls_party_service_for_respondent(self):
        pass







