import unittest
from unittest.mock import patch
from app.services.service_toggles import Party, Case
from app.api_mocks.party_service_mock import PartyServiceMock
from app.services.party_service import PartyService
import logging
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

class ServiceMockTestCase(unittest.TestCase):
    """Test case for toggling between a service and its mock"""

    def test_use_mock_service_uses_mock(self):
        """Test can use mock """
        sut = Party(False)
        sut.use_mock_service()
        self.assertTrue(isinstance(sut._service, PartyServiceMock))

    def test_use_real_service_uses_real_service(self):
        """Test can use real service"""
        sut = Party(False)
        sut.use_real_service()
        self.assertTrue(isinstance(sut._service, PartyService))

    def test_can_change_type_after_init(self):
        """Test can change after init"""
        sut = Party(False)
        sut.use_real_service()
        sut.use_mock_service()
        sut.use_real_service()
        sut.use_mock_service()
        self.assertTrue(isinstance(sut._service, PartyServiceMock))

    @patch.object(logger, 'debug')
    def test_changing_to_non_mocked_party_service_results_calls_logger(self, logger_debug):
        """Validate that the logger is called if real party service is used"""
        sut = Party(False)
        sut.use_real_service()
        logger_debug.assert_called()

    @patch.object(logger, 'debug')
    def test_changing_to_mocked_party_service_results_calls_logger(self, logger_debug):
        """Validate that the logger is called if mocked party service is used"""
        sut = Party(False)
        sut.use_mock_service()
        logger_debug.assert_called()

    @patch.object(logger, 'debug')
    def test_changing_to_non_mocked_case_service_results_calls_logger(self, logger_debug):
        """Validate that the logger is called if real party service is used"""
        sut = Case(False)
        sut.use_real_service()
        logger_debug.assert_called()

    @patch.object(logger, 'debug')
    def test_changing_to_mocked_case_service_results_calls_logger(self, logger_debug):
        """Validate that the logger is called if mocked party service is used"""

        sut = Case(False)
        sut.use_mock_service()
        logger_debug.assert_called()