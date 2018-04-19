from flask import request, jsonify, g
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.saver import Saver
from secure_message.resources.messages import MessageSend
from secure_message.v2.validation.domain import MessageSchemaV2, logger
from secure_message.v2.repository.retriever import RetrieverV2

# todo change these to be one class


class MessageCounterV2(Resource):
    """Get count of unread messages using v2 endpoint"""
    @staticmethod
    def get():
        if request.args.get('label'):
            name = str(request.args.get('label'))
            survey = request.args.get('survey')
            if name.lower() == 'unread':
                message_service = RetrieverV2()
                return jsonify(name=name, total=message_service.unread_message_count_by_survey(g.user, survey))
            else:
                logger.debug('Invalid label name', name=name, request=request.url)
                raise BadRequest(description="Invalid label")
        else:
            logger.debug('No Name parameter specified in URL', request=request.url)
            raise BadRequest(description='No Label Name Parameter specified.')
