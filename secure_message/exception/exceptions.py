import logging
import os
import sys

from structlog import wrap_logger
from werkzeug.exceptions import HTTPException

from secure_message import settings

"""Specialised exceptions for secure messages"""

logger = wrap_logger(logging.getLogger(__name__))


class MessageSaveException(HTTPException):

    """ This exception is used when the service fails to save a secure message"""

    code = 500

    def __init__(self, message, code=None):
        HTTPException.__init__(self)
        self.description = message
        if code is not None:
            self.code = code


class RasNotifyException(MessageSaveException):
    def __init__(self, code=500):
        MessageSaveException.__init__(self, 'There was a problem sending a notification via RM Notify-Gateway to '
                                            'GOV.UK Notify', code=code)
        logger.error(self.description)


class MissingEnvironmentVariable(Exception):
    def __init__(self):
        missing_env_variables = [var for var in settings.NON_DEFAULT_VARIABLES if not os.environ.get(var)]
        logger.error('Missing environment variables', variables=missing_env_variables)
        sys.exit("Application failed to start")
