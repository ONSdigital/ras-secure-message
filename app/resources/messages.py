from flask_restful import Resource
from flask import request, jsonify
from app.domain_model.domain import MessageSchema
from app.repository.saver import Saver
from app.repository.retriever import Retriever
import logging
from app.common.alerts import AlertUser
from app import settings
from app.settings import MESSAGE_QUERY_LIMIT

logger = logging.getLogger(__name__)

MESSAGE_LIST_ENDPOINT = "messages"
MESSAGE_BY_ID_ENDPOINT = "message"

"""Rest endpoint for message resources. Messages are immutable, they can only be created and archived."""


class MessageList(Resource):

    """Return a list of messages for the user"""

    @staticmethod
    def get():
        # res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            page = 1
            limit = MESSAGE_QUERY_LIMIT

            if request.args.get('limit') and request.args.get('page'):
                page = int(request.args.get('page'))
                limit = int(request.args.get('limit'))

            message_service = Retriever()
            status, result = message_service.retrieve_message_list(page, limit)
            if status:
                resp = MessageList._paginated_list_to_json(result, page, limit, request.host_url)
                resp.status_code = 200
                return resp
        else:
            return res

    @staticmethod
    def _paginated_list_to_json(paginated_list, page, limit, host_url):
        messages = {}
        msg_count = 0
        for message in paginated_list.items:
            msg_count += 1
            msg = message.serialize
            msg['_links'] = {"self": {"href": "{0}{1}/{2}".format(host_url, MESSAGE_BY_ID_ENDPOINT, msg['id'])}}
            messages["{0}".format(msg_count)] = msg

        links = {
            'first': {"href": "{0}{1}".format(host_url, "messages")},
            'self': {"href": "{0}{1}?page={2}&limit={3}".format(host_url, MESSAGE_LIST_ENDPOINT, page, limit)}
        }

        if paginated_list.has_next:
            links['next'] = {
                "href": "{0}{1}?page={2}&limit={3}".format(host_url, MESSAGE_LIST_ENDPOINT, (page + 1), limit)}

        if paginated_list.has_prev:
            links['prev'] = {
                "href": "{0}{1}?page={2}&limit={3}".format(host_url, MESSAGE_LIST_ENDPOINT, (page - 1), limit)}

        return jsonify({"messages": messages, "_links": links})


class MessageSend(Resource):
    """Send message for a user"""

    @staticmethod
    def post():
        logger.info("Message send POST request.")
        message = MessageSchema().load(request.get_json())
        if message.errors == {}:
            Saver().save_message(message.data)
            return MessageSend._alert_recipients(message.data.msg_id)
        else:
            res = jsonify(message.errors)
            res.status_code = 400
            return res

    @staticmethod
    def _alert_recipients(reference):
        recipient_email = settings.NOTIFICATION_DEV_EMAIL  # TODO change this when know more about party service
        alert_user = AlertUser()
        alert_status, alert_detail = alert_user.send(recipient_email, reference)
        resp = jsonify({'status': '{0}'.format(alert_detail)})
        resp.status_code = alert_status
        return resp


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
