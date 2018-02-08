import logging

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def set_v2_resources(api):
    """v2 endpoints """
