import unittest
from unittest.mock import patch
from app.services.service_toggles import party
from app.api_mocks.party_service_mock import PartyServiceMock
from app.services.party_service import PartyService
import logging
from flask import json


class PartyServiceIntegrationTestCase(unittest.TestCase):
    """Test case for toggling between a service and its mock"""

    @unittest.SkipTest
    def test_calling_get_business_data_for_non_existent_business_returns_expected_message(self):
        """Asking for business not in test data gives expected response"""
        sut = party
        sut.use_real_service()
        expected = {"errors": "Business with party id '0a6018a0-3e67-4407-b120-780932434b36' does not exist."}
        response = sut.get_business_details('0a6018a0-3e67-4407-b120-780932434b36')
        self.assertEqual(json.loads(response.data), expected)

    @unittest.SkipTest
    def test_calling_get_business_data_for_invalid_format_id_returns_expected_message(self):
        """Using invalid format_for_id gives expected error """
        sut = party
        sut.use_real_service()
        expected = {'errors': "'14900000000' is not a valid UUID format for property 'id'."}
        response = sut.get_business_details('14900000000')
        response_data = json.loads(response.data)
        self.assertEqual(response_data, expected)

    @unittest.SkipTest
    def test_calling_get_business_data_returns_expected_message(self):
        """Using id expected in test data results in expected data returned"""
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

    @unittest.SkipTest
    def test_calling_get_user_data_for_non_existent_user_returns_expected_message(self):
        """test non existi=ant user returns expected error message"""

        sut = party
        sut.use_real_service()
        expected = {"errors": "Respondent with party id '0a6018a0-3e67-4407-b120-780932434b36' does not exist."}
        response = sut.get_user_details('0a6018a0-3e67-4407-b120-780932434b36')
        self.assertEqual(json.loads(response.data), expected)

    @unittest.SkipTest
    def test_calling_get_respondent_data_with_expected_test_data_returns_expected_message(self):
        """Test expected test user data returned when requested"""
        sut = party
        sut.use_real_service()
        expected = {"id": "db036fd7-ce17-40c2-a8fc-932e7c228397",
                    "emailAddress": "testuser@email.com",
                    "firstName": "Test",
                    "lastName": "User",
                    "telephone": "1234",
                    "sampleUnitType": "BI"
                    }
        response = sut.get_user_details("db036fd7-ce17-40c2-a8fc-932e7c228397")
        self.assertEqual(json.loads(response.data), expected)
