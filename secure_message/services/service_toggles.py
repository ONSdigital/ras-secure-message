import logging

from structlog import wrap_logger

from secure_message.api_mocks.internal_user_service_mock import InternalUserServiceMock
from secure_message.api_mocks.party_service_mock import PartyServiceMock
from secure_message.services.internal_user_service import InternalUserService
from secure_message.services.party_service import PartyService

#
# A ServiceMockToggle is intended to support switching between a Mock and a Real Service without the
# client code being impacted . Typical use is to define a class which knows about the mock and real service
# Default to use the real service , and call use_mock_service in test scenarios
# Client code is still free to call the mock directly , but this should be in tests only
#

logger = wrap_logger(logging.getLogger(__name__))


class ServiceMockToggle:
    """A ServiceMockToggle is a common base class intended to be used to switch between a service and its Mock"""

    def __init__(self, use_mock, real_service, mock_service, service_name):
        self._service = None
        self._service_name = service_name
        self._real_service = real_service()
        self._mock_service = mock_service()
        self.use_mock_service() if use_mock else self.use_real_service()

    def use_mock_service(self):
        self._service = self._mock_service
        logger.debug("Mocked service in use", service_name=self._service_name)

    def use_real_service(self):
        self._service = self._real_service
        logger.debug("Non mocked service in use", service_name=self._service_name)

    @property
    def using_mock(self):
        return self._service == self._mock_service


class Party(ServiceMockToggle):
    """A Party acts as an interface to mocked or real Party Services via its ServiceMockToggle base"""

    def __init__(self, use_mock=False):
        super().__init__(use_mock, PartyService, PartyServiceMock, "Party")

    def get_business_details(self, business_ids):
        return self._service.get_business_details(business_ids)

    def get_user_details(self, uuid):
        return self._service.get_user_details(uuid)

    def get_users_details(self, uuids):
        return self._service.get_users_details(uuids)

    def does_user_have_claim(self, user_id, business_id, survey_id):
        return self._service.does_user_have_claim(user_id, business_id, survey_id)


class InternalUser(ServiceMockToggle):
    """An internal user service mock to authenticate users"""

    def __init__(self, use_mock=False):
        super().__init__(use_mock, InternalUserService, InternalUserServiceMock, "InternalUser")

    def get_user_details(self, user_details):
        return self._service.get_user_details(user_details)


party = Party(False)

internal_user_service = InternalUser(False)
