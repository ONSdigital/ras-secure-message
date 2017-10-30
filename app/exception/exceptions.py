import logging
import os
import sys

from structlog import wrap_logger

from app import settings

"""Specialised exceptions for secure messages"""

logger = wrap_logger(logging.getLogger(__name__))


class MessageSaveException(Exception):

    """ This exception is used when the service fails to save a secure message"""

    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class RasNotifyException(MessageSaveException):
    pass


class MissingEnvironmentVariable(Exception):
    def __init__(self):
        missing_env_variables = [var for var in settings.NON_DEFAULT_VARIABLES if not os.environ.get(var)]
        logger.error('Missing environment variables', variables=missing_env_variables)
        sys.exit("Application failed to start")
