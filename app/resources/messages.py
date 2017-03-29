from flask_restful import Resource
from flask import request, Response, jsonify
from app.domain_model.domain import MessageSchema
from app.repository.saver import Saver
from app.repository.retriever import Retriever
import logging
from app.common.alerts import AlertUser, AlertViaGovNotify
from app import settings

logger = logging.getLogger(__name__)

"""Rest endpoint for message resources. Messages are immutable, they can only be created and archived."""


class MessageList(Resource):

    """Return a list of messages for the user"""
    @staticmethod
    def get():
        # res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            message_service = Retriever()
            # msg_list = message_service.retrieve_message_list()
            resp = message_service.retrieve_message_list()
            resp.status_code = 200
            return resp
        else:
            return res


class MessageSend(Resource):
    """Send message for a user"""

    @staticmethod
    def alert_recipients():
        recipient_email = settings.NOTIFICATION_DEV_EMAIL  # change this when know more about party service
        alerter = AlertUser(AlertViaGovNotify())
        alerter.send(recipient_email, settings.NOTIFICATION_TEMPLATE_ID, None)

    @staticmethod
    def post():
        # res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            logger.info("Message send POST request.")
            message = MessageSchema().load(request.get_json())
            if message.errors == {}:
                message_service = Saver()
                message_service.save_message(message.data)
                resp = jsonify({'status': "ok"})
                resp.status_code = 201
                # self.alert_recipients()
                return resp
            else:
                res = Response(response=message.errors, status=400, mimetype="text/html")
                return res
        else:
            return res


class MessageById(Resource):

    """Get message by id"""
    @staticmethod
    def get(message_id):
        # res = authenticate(request)
        message_service = Retriever()
        resp = message_service.retrieve_message(message_id)
        return resp

    """Update message by id"""
    @staticmethod
    def put():
        resp = jsonify({"status": "ok"})
        resp.status_code = 200
        return resp
