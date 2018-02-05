import logging

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class InternalUserService:
    @staticmethod
    def get_user_details(uuid):
        """gets the user details from the internal user service"""
        logger.debug("getting user details from uaa")
        pass
