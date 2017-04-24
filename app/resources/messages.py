# from app.authentication.jwt import decode
from flask_restful import Resource
from flask import request, jsonify
from werkzeug.exceptions import BadRequest

from app.repository.modifier import Modifier
from app.validation.domain import MessageSchema
from app.repository.saver import Saver
from app.repository.retriever import Retriever

import logging
from app.common.alerts import AlertUser
from app import settings
from app.settings import MESSAGE_QUERY_LIMIT
from app.validation.labels import Labels
from app.validation.user import User
from datetime import timezone, datetime

logger = logging.getLogger(__name__)

MESSAGE_LIST_ENDPOINT = "messages"
MESSAGE_BY_ID_ENDPOINT = "message"

"""Rest endpoint for message resources. Messages are immutable, they can only be created."""


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
                resp = MessageList._paginated_list_to_json(result, page, limit, request.host_url,
                                                           request.headers.get('user_urn'))
                resp.status_code = 200
                return resp
        else:
            return res

    @staticmethod
    def _paginated_list_to_json(paginated_list, page, limit, host_url, user_urn):
        """used to change a pagination object to json format with links"""
        messages = {}
        msg_count = 0
        for message in paginated_list.items:
            msg_count += 1
            msg = message.serialize(user_urn)
            msg['_links'] = {"self": {"href": "{0}{1}/{2}".format(host_url, MESSAGE_BY_ID_ENDPOINT, msg['msg_id'])}}
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
            return MessageSend.message_save(message)
        else:
            res = jsonify(message.errors)
            res.status_code = 400
            return res

    @staticmethod
    def message_save(message):
        """Saves the message to the database along with the subsequent status and audit"""
        save = Saver()
        save.save_message(message.data, datetime.now(timezone.utc))
        if User(message.data.urn_from).is_respondent:
            save.save_msg_status(message.data.urn_from, message.data.msg_id, Labels.SENT.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.UNREAD.value)
        else:
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.SENT.value)
            save.save_msg_audit(message.data.msg_id, message.data.urn_from)
            save.save_msg_status(message.data.urn_to, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.urn_to, message.data.msg_id, Labels.UNREAD.value)

        return MessageSend._alert_recipients(message.data.msg_id)

    @staticmethod
    def _alert_recipients(reference):
        """used to alert user once messages have been saved"""
        recipient_email = settings.NOTIFICATION_DEV_EMAIL  # TODO change this when know more about party service
        alert_user = AlertUser()
        alert_status, alert_detail = alert_user.send(recipient_email, reference)
        resp = jsonify({'status': '{0}'.format(alert_detail)})
        resp.status_code = alert_status
        return resp


class MessageById(Resource):
    """Get and update message by id"""

    @staticmethod
    def get(message_id):
        """Get message by id"""
        # res = authenticate(request)
        user_urn = request.headers.get('user_urn')  # getting user urn from header request
        # check user is authorised to view message
        message_service = Retriever()
        # pass msg_id and user urn
        resp = message_service.retrieve_message(message_id, user_urn)
        return jsonify(resp)


class ModifyById(Resource):
    """Update message status by id"""


    @staticmethod
    def put(message_id):
        """Update message by status"""
        user_urn = request.headers.get('user_urn')

        request_data = request.get_json()
        if request_data["label"] not in Labels.label_list.value:
            raise BadRequest(description="Invalid label given")

        if request_data["action"] != "add" and request_data["action"] != "remove":
            raise BadRequest(description="Invalid action taken")

        message_service = Retriever()
        # pass msg_id and user urn
        message = message_service.retrieve_message(message_id, user_urn)
        modifier = Modifier()
        resp = False

        if request_data['action'] == 'add' and request_data['label'] == 'ARCHIVE':
            resp = modifier.add_archived(message, user_urn)

        elif request_data['action'] == 'remove' and request_data['label'] == 'ARCHIVE':
            resp = modifier.del_archived(message, user_urn)

        elif request_data['action'] == 'add' and request_data['label'] == 'UNREAD':
            resp = modifier.add_unread(message, user_urn)

        elif request_data['action'] == 'remove' and request_data['label'] == 'UNREAD':
            resp = modifier.del_unread(message, user_urn)

        if resp:
            res = jsonify({'status':'ok'})
            res.status_code = 200
            return res
