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


class MessageSendV2(MessageSend):

    """Send A message using the V2 endpoint"""
    def post(self):     # expose endpoint as a resource
        return super(MessageSendV2, self).post()

    @staticmethod
    def _message_save(message):
        """Saves the message to the database along with the subsequent status and audit"""
        save = Saver()
        save.save_message(message.data)
        save.save_msg_event(message.data.msg_id, EventsApi.SENT.value)

        save.save_msg_status(message.data.msg_from, message.data.msg_id, Labels.SENT.value)
        save.save_msg_status(message.data.msg_to[0], message.data.msg_id, Labels.INBOX.value)
        save.save_msg_status(message.data.msg_to[0], message.data.msg_id, Labels.UNREAD.value)

    @staticmethod
    def _validate_post_data(post_data):
        message = MessageSchemaV2().load(post_data)
        return message


class MessageCounterV2(Resource):
    """Get count of unread messages using v2 endpoint"""
    @staticmethod
    def get():
        survey = request.args.getlist('survey')
        if request.args.get('label'):
            label = str(request.args.get('label'))
            if label.lower() == 'unread':
                message_service = RetrieverV2()
                return jsonify(name=label, total=message_service.message_count_by_survey(g.user, survey, label))
            else:
                logger.debug('Invalid label name', name=label, request=request.url)
                raise BadRequest(description="Invalid label")
        else:
            label = None
            message_service = RetrieverV2()
            return jsonify(total=message_service.message_count_by_survey(g.user, survey, label))
