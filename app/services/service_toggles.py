from app.api_mocks.party_service_mock import PartyServiceMock
from app.services.party_service import PartyService
import logging
from structlog import wrap_logger

#
# A ServiceMockToggle is intended to support switching between a Mock and a Real Service without the
# client code being impacted . Typical use is to define a class which knows about the mock and real service
# Default to use the real service , and call use_mock_service in test scenarios
# Client code is still free to call the mock directly , but this should be in tests only
#

logger = wrap_logger(logging.getLogger(__name__))


class ServiceMockToggle:
    """ A ServiceMockToggle is a common base class intended to be used to switch between a service and its Mock"""

    def __init__(self, use_mock, real_service, mock_service, service_name):
        self._service = None
        self._service_name = service_name
        self._real_service = real_service()
        self._mock_service = mock_service()
        self.use_mock_service() if use_mock else self.use_real_service()

    def use_mock_service(self):
        self._service = self._mock_service
        logger.debug('Mocked service in use', service_name=self._service_name)

    def use_real_service(self):
        self._service = self._real_service
        logger.debug('Non mocked service in use', service_name=self._service_name)


class Party(ServiceMockToggle):
    """A Party acts as an interface to mocked or real Party Services via its ServiceMockToggle base"""

    def __init__(self, use_mock=False):
        super().__init__(use_mock, PartyService, PartyServiceMock, 'Party')

    def get_business_details(self, ru):
        return self._service.get_business_details(ru)

    def get_user_details(self, uuid):
        return self._service.get_user_details(uuid)

"""party is the interface that code should use mocktoggle for the party service """
party = Party(False)



