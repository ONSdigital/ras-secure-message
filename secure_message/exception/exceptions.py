import logging
import os
import sys

from structlog import wrap_logger
from werkzeug.exceptions import HTTPException

logger = wrap_logger(logging.getLogger(__name__))


class MessageSaveException(HTTPException):

    """ This exception is used when the service fails to save a secure message"""

    code = 500

    def __init__(self, message, survey_id=None, party_id=None, status_code=None):
        HTTPException.__init__(self)
        self.description = message, survey_id, party_id
        if status_code is not None:
            self.code = status_code


class RasNotifyException(MessageSaveException):
    def __init__(self, survey_id, party_id, code=500):
        MessageSaveException.__init__(self, 'There was a problem sending a notification via RM Notify-Gateway to '
                                            'GOV.UK Notify', survey_id=survey_id, party_id=party_id, status_code=code)
        logger.error(self.description)


class MissingEnvironmentVariable(Exception):
    def __init__(self, defaults):      # pylint:disable=super-init-not-called
        missing_env_variables = [var for var in defaults if not os.environ.get(var)]
        logger.error('Missing environment variables', variables=missing_env_variables)
        sys.exit("Application failed to start")
