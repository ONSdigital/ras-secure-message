import logging
import os
import sys
import flask

from flask import g

from structlog import configure
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level, filter_by_level


def logger_initial_config():
    logger_date_format = os.getenv('LOGGING_DATE_FORMAT', "%Y-%m-%dT%H:%M%s")
    logger_format = "%(message)s"
    log_level = os.getenv('SMS_LOG_LEVEL', 'DEBUG')
    service_name = 'ras-secure-message'
    try:
        indent = int(os.getenv('JSON_INDENT_LOGGING'))
    except (TypeError, ValueError):
        indent = None

    def add_service(_1, _2, event_dict):
        """
        Add the service name to the event dict.
        """
        event_dict['service'] = service_name
        return event_dict


    logging.basicConfig(stream=sys.stdout,
                        level=log_level,
                        format=logger_format)
    configure(processors=[add_log_level,
                          filter_by_level,
                          add_service,
                          TimeStamper(fmt=logger_date_format, utc=True, key="created_at"),
                          JSONRenderer(indent=indent)])
