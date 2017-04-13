from app.authentication.jwt import decode
from flask_restful import Resource
from flask import request, jsonify, Response
from sqlalchemy import engine
from app import constants
from app.validation.domain import MessageSchema
from app.repository.saver import Saver
from app.repository.retriever import Retriever
import logging
import uuid
from app.common.alerts import AlertUser
from app import settings
from app.settings import MESSAGE_QUERY_LIMIT

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
                resp = MessageList._paginated_list_to_json(result, page, limit, request.host_url)
                resp.status_code = 200
                return resp
        else:
            return res

    @staticmethod
    def _paginated_list_to_json(paginated_list, page, limit, host_url):
        """used to change a pagination object to json format with links"""
        messages = {}
        msg_count = 0
        for message in paginated_list.items:
            msg_count += 1
            msg = message.serialize
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

        validated_message = MessageSend.validate_message(request, message)

        if validated_message.errors == {}:
            post = request.get_json()
            Saver().save_message(message.data)
            Saver().save_msg_status(post['urn_from'], post['msg_id'], constants.LABEL_SENT)
            Saver().save_msg_status(post['urn_to'], post['msg_id'], constants.LABEL_INBOX)
            Saver().save_msg_status(post['urn_to'], post['msg_id'], constants.LABEL_UNREAD)
            return MessageSend._alert_recipients(message.data.msg_id)
        else:
            res = jsonify(message.errors)
            res.status_code = 400
            return res

    @staticmethod
    def _alert_recipients(reference):
        """used to alert user once messages have been saved"""
        recipient_email = settings.NOTIFICATION_DEV_EMAIL  # TODO change this when know more about party service
        alert_user = AlertUser()
        alert_status, alert_detail = alert_user.send(recipient_email, reference)
        resp = jsonify({'status': '{0}'.format(alert_detail)})
        resp.status_code = alert_status
        return resp

    @staticmethod
    def validate_message(request1, message):
        if 'urn_to' not in request1.get_json() or len(request1.get_json()['urn_to']) == 0:
            message.errors.update({'urn_to': 'Expected a urn_to field to be given'})
        elif len(request1.get_json()['urn_to']) >= constants.MAX_TO_LEN:
            message.errors.update({'urn_to': 'Expected a urn_to field to with character length under 100'})

        if 'urn_from' not in request1.get_json() or len(request1.get_json()['urn_from']) == 0:
            message.errors.update({'urn_from': 'Expected a urn_from field to be given'})
        elif len(request1.get_json()['urn_from']) >= constants.MAX_FROM_LEN:
            message.errors.update({'urn_from': 'Expected a urn_from field to with character length under 100'})

        return message


class MessageById(Resource):
    """Get and update message by id"""

    @staticmethod
    def get(message_id):
        """Get message by id"""
        # res = authenticate(request)
        message_service = Retriever()
        resp = message_service.retrieve_message(message_id)
        return resp

    @staticmethod
    def put():
        pass

# class MessageStatus(Resource):
#     """Ability to add and delete labels for a message."""
#
#     @staticmethod
#     def get(message_id):
#         """Get message by id"""
#         # res = authenticate(request)
#         message_service = Retriever()
#         resp = message_service.retrieve_message(message_id)
#         return resp
#
#     @staticmethod
#     def put(request):
#         """Update message by status"""
#
#         # user_urn = str(uuid.uuid4())
#
#         if request.headersb.get('urn'):
#             urn_token = request.headers.get('urn')
#             return urn_token
#
#         msg_id = str(uuid.uuid4())
#         query = 'INSERT INTO status VALUES ("1","INBOX,UNREAD","get.msg_id","user_urn")'.format(urn_token,msg_id)
#         with engine.connect() as con:
#             con.execute(query)
#
#         resp = jsonify({"status": "ok"})
#
#         resp.status_code = 200
#         return resp
