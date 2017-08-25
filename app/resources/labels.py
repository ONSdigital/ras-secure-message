import logging

from flask_restful import Resource
from flask import request
from app.repository.retriever import Retriever
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest

logger = wrap_logger(logging.getLogger(__name__))


class Labels(Resource):
    @staticmethod
    def get():
        """Get count of unread messages"""

        if request.args.get('name'):
            name = str(request.args.get('name'))

        if name.lower() == 'unread':
            message_service = Retriever()
            return  message_service.unread_message_count()
        raise BadRequest(description="Invalid label")