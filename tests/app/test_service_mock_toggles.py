import unittest

from secure_message.services.service_toggles import Party
from secure_message.api_mocks.party_service_mock import PartyServiceMock
from secure_message.services.party_service import PartyService


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
