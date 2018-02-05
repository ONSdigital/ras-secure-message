import logging

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class InternalUserServiceMock:
    @staticmethod
    def get_user_details(uuid):
        """gets the user details from the internal user service"""
        logger.debug("getting mock user details for uaa")
        if uuid:
            internal_user_dict = {"id": uuid,
                                  "firstName": "fred",
                                  "lastName": "flinstone",
                                  "emailAddress": "mock@email.com"}
            return internal_user_dict, 200
        else:
            return "error retrieving details"
