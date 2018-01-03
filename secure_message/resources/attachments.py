import logging

from flask_restful import Resource
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class Attachments(Resource):
    """Attachments class"""
    def get(self):
        pass