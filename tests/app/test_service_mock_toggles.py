import unittest
from unittest.mock import patch
from app.services.service_toggles import party
from app.api_mocks.party_service_mock import PartyServiceMock
from app.services.party_service import PartyService
import logging
from flask import json


class ServiceMockTestCase(unittest.TestCase):
    """Test case for toggling between a service and its mock"""

    def test_use_mock_service_uses_mock(self):
        """Test can use mock """
        party.use_mock_service()
        self.assertTrue(isinstance(party._service, PartyServiceMock))

    def test_use_real_service_uses_real_service(self):
        """Test can use real service"""
        party.use_real_service()
        self.assertTrue(isinstance(party._service, PartyService))

    def test_can_change_type_after_init(self):
        """Test can change after init"""
        party.use_real_service()
        party.use_mock_service()
        party.use_real_service()
        party.use_mock_service()
        self.assertTrue(isinstance(party._service, PartyServiceMock))

    @patch.object(logging.Logger, 'debug')
    def test_changing_to_non_mocked_party_service_results_calls_logger(self, logger_debug):
        """Validate that the logger is called correctly if real party service is used"""
        party.use_real_service()
        logger_debug.assert_called_with("event='Non mocked Party service in use'")

    @patch.object(logging.Logger, 'debug')
    def test_changing_to_mocked_party_service_results_calls_logger(self, logger_debug):
        """Validate that the logger is called correctly if mocked party service is used"""
        party.use_mock_service()
        logger_debug.assert_called_with("event='Mocked Party service in use'")

    def test_calling_get_business_data_from_mock_returns_expected_json(self):
        party.use_mock_service()
        expected = json.loads('{"ru_id": "c614e64e-d981-4eba-b016-d9822f09a4fb","name": "AOL"}')
        party_response = party.get_business_details('c614e64e-d981-4eba-b016-d9822f09a4fb')
        result = json.loads(party_response.data)
        self.assertTrue(result == expected)

    @unittest.SkipTest
    def test_calling_get_business_data_from_actual_for_non_existent_business_returns_expected_message(self):
        sut = party
        sut.use_real_service()
        expected = {"errors": "Business with party id '0a6018a0-3e67-4407-b120-780932434b36' does not exist."}
        response = sut.get_business_details('0a6018a0-3e67-4407-b120-780932434b36')
        self.assertEqual(json.loads(response.data), expected)

    @unittest.SkipTest
    def test_calling_get_business_data_from_actual_forinvalid_format_id_returns_expected_message(self):
        sut = party
        sut.use_real_service()
        expected = {'errors': "'14900000000' is not a valid UUID format for property 'id'."}
        response = sut.get_business_details('14900000000')
        response_data = json.loads(response.data)
        self.assertEqual(response_data, expected)

    @unittest.SkipTest
    def test_calling_get_business_data_from_expected_test_data_business_returns_expected_message(self):
        sut = party
        sut.use_real_service()

        expected = {"attributes": {},
                    "businessRef": "49900000000",
                    "contactName": "Test User",
                    "employeeCount": 50,
                    "enterpriseName": "ABC Limited",
                    "facsimile": "+44 1234 567890",
                    "fulltimeCount": 35,
                    "id": "3b136c4b-7a14-4904-9e01-13364dd7b972",
                    "legalStatus": "Private Limited Company",
                    "name": "Bolts and Ratchets Ltd",
                    "sampleUnitType": "B",
                    "sic2003": "2520",
                    "sic2007": "2520",
                    "telephone": "+44 1234 567890",
                    "tradingName": "ABC Trading Ltd",
                    "turnover": 350
                    }

        response = sut.get_business_details('3b136c4b-7a14-4904-9e01-13364dd7b972')

        self.assertTrue(json.loads(response.data) == expected)
