import logging

from structlog import wrap_logger

from secure_message.constants import NON_SPECIFIC_INTERNAL_USER
from secure_message.services.internal_user_service import InternalUserService

logger = wrap_logger(logging.getLogger(__name__))


class InternalUserServiceMock:
    def __init__(self):
        self.internal_user_dict = {
            "Someuuid": {
                "id": "Someuuid",
                "firstName": "fred",
                "lastName": "flinstone",
                "emailAddress": "mock@email.com",
            },
            "01b51fcc-ed43-4cdb-ad1c-450f9986859b": {
                "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
                "firstName": "fred",
                "lastName": "flinstone",
                "emailAddress": "mock@email.com",
            },
            "f62dfda8-73b0-4e0e-97cf-1b06327a6712": {
                "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
                "firstName": "fred",
                "lastName": "flinstone",
                "emailAddress": "mock@email.com",
            },
            "ce12b958-2a5f-44f4-a6da-861e59070a31": {
                "id": "ce12b958-2a5f-44f4-a6da-861e59070a31",
                "firstName": "Selphie",
                "lastName": "Tilmitt",
                "emailAddress": "selphie@mockemail.com",
            },
            "Tej": {"id": "Tej", "firstName": "Tejas", "lastName": "patel", "emailAddress": "mock@email.com"},
            "BRES": {"id": "BRES", "firstName": "BRES", "lastName": "", "emailAddress": "mock@email.com"},
            "SpecificInternalUserId": {
                "id": "SpecificInternalUserId",
                "firstName": "Internal",
                "lastName": "User",
                "emailAddress": "mock@email.com",
            },
            "AlternateSpecificInternalUserId": {
                "id": "AlternateSpecificInternalUserId",
                "firstName": "alternate",
                "lastName": "Internal_user",
                "emailAddress": "mock@email.com",
            },
        }

    def get_user_details(self, uuid):
        """gets the user details from the internal user service"""
        found = None
        if uuid:
            if uuid == NON_SPECIFIC_INTERNAL_USER:
                return InternalUserService.get_default_user_details(NON_SPECIFIC_INTERNAL_USER)
            found = self.internal_user_dict.get(uuid)
            if not found:
                err_string = f"error retrieving details for {uuid}"
                logger.error(err_string)

        return found
