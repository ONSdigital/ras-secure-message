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
