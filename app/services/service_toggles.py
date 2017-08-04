from app.api_mocks.party_service_mock import PartyServiceMock
from app.services.party_service import PartyService

#
# A ServiceMockToggle is intended to support switching between a Mock and a Real Service without the
# client code knowing . Typical use is to define a class which knows about the mock and real service
# Default to use the real service , and call use_mock_service in test scenarios
# Client code is still free to call the mock directly , but this should be in tests only
#

class ServiceMockToggle:
    """ A ServiceMockToggle is a common base class intended to be used to switch between a service and its Mock"""
    service = None

    def __init__(self, use_mock, real_service, mock_service):
        self._real_service = real_service()
        self._mock_service = mock_service()
        self.use_mock_service() if use_mock else self.use_real_service()

    def use_mock_service(self):
        ServiceMockToggle.service = self._mock_service

    def use_real_service(self):
        ServiceMockToggle.service = self._real_service


class Party(ServiceMockToggle):
    """A Party acts as an interface to mocked or read Party Services via its ServiceMockToggle base"""

    def __init__(self, use_mock=False):
        super().__init__(use_mock, PartyService, PartyServiceMock)

    def get_business_details(self, ru):
        return super().service.get_business_details(ru)

    def get_user_details(self, uuid):
        return super().service.get_user_details(uuid)

"""party is the point of use for the mocktoggle for the party service """
party = Party(False)
