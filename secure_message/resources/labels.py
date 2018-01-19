import logging

from flask_restful import Resource
from flask import request, g, jsonify
from secure_message.repository.retriever import Retriever
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
                return jsonify(name=name, total=message_service.unread_message_count(g.user))
            else:
                logger.debug('Invalid label name', name=name, request=request.url)
                raise BadRequest(description="Invalid label")
        else:
            logger.debug('No Name parameter specified in URL', request=request.url)
            raise BadRequest(description='No Label Name Paramter specified.')
