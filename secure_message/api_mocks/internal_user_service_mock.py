import logging

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class InternalUserServiceMock:
    def __init__(self):
        self.internal_user_dict = {"Someuuid": {"id": "Someuuid",
                                                "firstName": "fred",
                                                "lastName": "flinstone",
                                                "emailAddress": "mock@email.com"}}

    def get_user_details(self, uuid):
        """gets the user details from the internal user service"""
        logger.debug("getting mock user details for uaa")
        if uuid:
            return self.internal_user_dict[uuid], 200
        return "error retrieving details"
