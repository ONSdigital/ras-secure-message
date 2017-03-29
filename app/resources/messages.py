from flask_restful import Resource
from flask import request
from flask import jsonify
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

    _alertMethod = AlertViaGovNotify()

    @property                   # By using a property we can inject an alerter during test
    def alert_method(self):
        return self._alertMethod

    @alert_method.setter
    def alert_method(self, value):
        self._alertMethod = value

    def alert_recipients(self):
        recipient_email = settings.NOTIFICATION_DEV_EMAIL  # TODO change this when know more about party service
        alert_user = AlertUser(self.alert_method)
        alert_status, alert_detail = alert_user.send(recipient_email, settings.NOTIFICATION_TEMPLATE_ID, None)
        resp = jsonify({'status': '{0}'.format(alert_detail)})
        resp.status_code = alert_status
        return resp

    def post(self):
        logger.info("Message send POST request.")
        message = MessageSchema().load(request.get_json())
        Saver().save_message(message.data)
        return self.alert_recipients( )



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
