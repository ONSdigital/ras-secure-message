import logging

from flask import request, jsonify, g, Response
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import settings
from app.common.alerts import AlertUser
from app.common.labels import Labels
from app.repository.modifier import Modifier
from app.repository.retriever import Retriever
from app.repository.saver import Saver
from app.resources.drafts import DraftModifyById
from app.settings import MESSAGE_QUERY_LIMIT
from app.validation.domain import MessageSchema
from app.validation.user import User
from app.resources.drafts import DraftModifyById

logger = logging.getLogger(__name__)

MESSAGE_LIST_ENDPOINT = "messages"
MESSAGE_BY_ID_ENDPOINT = "message"

"""Rest endpoint for message resources. Messages are immutable, they can only be created."""


class MessageList(Resource):
    """Return a list of messages for the user"""

    @staticmethod
    def get():
        """Get message list with options"""
        string_query_args, page, limit, ru, survey, cc, label, desc = MessageList._get_options(request.args)

        message_service = Retriever()
        status, result = message_service.retrieve_message_list(page, limit, g.user_urn,
                                                               ru=ru, survey=survey, cc=cc, label=label, descend=desc)
        if status:
            resp = MessageList._paginated_list_to_json(result, page, limit, request.host_url,
                                                       g.user_urn, string_query_args)
            resp.status_code = 200
            return resp

    @staticmethod
    def _get_options(args):
        """extract options"""
        string_query_args = '?'
        page = 1
        limit = MESSAGE_QUERY_LIMIT
        ru = None
        survey = None
        cc = None
        label = None
        desc = True

        if args.get('limit'):
            limit = int(args.get('limit'))

        if args.get('page'):
            page = int(args.get('page'))

        if args.get('ru'):
            string_query_args = MessageList._add_string_query_args(string_query_args, 'ru', args.get('ru'))
            ru = str(args.get('ru'))
        if args.get('survey'):
            survey = str(args.get('survey'))
            string_query_args = MessageList._add_string_query_args(string_query_args, 'survey', args.get('survey'))
        if args.get('cc'):
            cc = str(args.get('cc'))
            string_query_args = MessageList._add_string_query_args(string_query_args, 'cc', args.get('cc'))
        if args.get('label'):
            label = str(args.get('label'))
            string_query_args = MessageList._add_string_query_args(string_query_args, 'label', args.get('label'))
        if args.get('desc'):
            desc = False if args.get('desc') == 'false' else True
            string_query_args = MessageList._add_string_query_args(string_query_args, 'desc', args.get('desc'))

        return string_query_args, page, limit, ru, survey, cc, label, desc

    @staticmethod
    def _add_string_query_args(string_query_args, arg, val):
        """Create query string for get messages options"""
        if string_query_args == '?':
            return '{0}{1}={2}'.format(string_query_args, arg, val)
        else:
            return '{0}&{1}={2}'.format(string_query_args, arg, val)

    @staticmethod
    def _paginated_list_to_json(paginated_list, page, limit, host_url, user_urn, string_query_args):
        """used to change a pagination object to json format with links"""
        messages = []
        msg_count = 0
        arg_joiner = ''
        if string_query_args != '?':
            arg_joiner = '&'

        for message in paginated_list.items:
            msg_count += 1
            msg = message.serialize(user_urn)
            msg['_links'] = {"self": {"href": "{0}{1}/{2}".format(host_url, MESSAGE_BY_ID_ENDPOINT, msg['msg_id'])}}
            messages.append(msg)

        links = {
            'first': {"href": "{0}{1}".format(host_url, "messages")},
            'self': {"href": "{0}{1}{2}{3}page={4}&limit={5}".format(host_url, MESSAGE_LIST_ENDPOINT, arg_joiner,
                                                                     string_query_args, page, limit)}
        }

        if paginated_list.has_next:
            links['next'] = {
                "href": "{0}{1}{2}{3}page={4}&limit={5}".format(host_url, MESSAGE_LIST_ENDPOINT, arg_joiner,
                                                                string_query_args, (page + 1), limit)}

        if paginated_list.has_prev:
            links['prev'] = {
                "href": "{0}{1}{2}{3}page={4}&limit={5}".format(host_url, MESSAGE_LIST_ENDPOINT, arg_joiner,
                                                                string_query_args, (page - 1), limit)}

        return jsonify({"messages": messages, "_links": links})


class MessageSend(Resource):
    """Send message for a user"""

    def post(self):
        """used to handle POST requests to send a message"""
        logger.info("Message send POST request.")
        post_data = request.get_json()
        is_draft = False
        returned_draft = None
        draft_id = None
        if 'msg_id' in post_data:
            is_draft, returned_draft = Retriever().check_msg_id_is_a_draft(post_data['msg_id'], g.user_urn)
            if is_draft is True:
                draft_id = post_data['msg_id']
                post_data['msg_id'] = ''
            else:
                raise (BadRequest(description="Message can not include msg_id"))

            last_modified = DraftModifyById.etag_check(request.headers, returned_draft)
            if last_modified is False:

                res = Response(response="Draft has been modified since last check", status=409,
                           mimetype="text/html")
                return res

        message = MessageSchema().load(post_data)
        if message.errors == {}:
            return self.message_save(message, is_draft, draft_id)
        else:
            resp = jsonify(message.errors)
            resp.status_code = 400
            return resp

    @staticmethod
    def del_draft_labels(draft_id):
        modifier = Modifier()
        modifier.del_draft(draft_id)

    def message_save(self, message, is_draft, draft_id):
        """Saves the message to the database along with the subsequent status and audit"""
        save = Saver()
        save.save_message(message.data)
        save.save_msg_event(message.data.msg_id, 'Sent')
        if User(message.data.urn_from).is_respondent:
            save.save_msg_status(message.data.urn_from, message.data.msg_id, Labels.SENT.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.UNREAD.value)
        else:
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.SENT.value)
            save.save_msg_audit(message.data.msg_id, message.data.urn_from)
            save.save_msg_status(message.data.urn_to, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.urn_to, message.data.msg_id, Labels.UNREAD.value)

        if is_draft is True:
            self.del_draft_labels(draft_id)
        return MessageSend._alert_recipients(message.data.msg_id)

    @staticmethod
    def _alert_recipients(reference):
        """used to alert user once messages have been saved"""
        recipient_email = settings.NOTIFICATION_DEV_EMAIL  # TODO change this when know more about party service
        alert_user = AlertUser()
        alert_status, alert_detail = alert_user.send(recipient_email, reference)
        resp = jsonify({'status': '{0}'.format(alert_detail), 'msg_id': reference})
        resp.status_code = alert_status
        return resp


class MessageById(Resource):
    """Get and update message by id"""

    @staticmethod
    def get(message_id):
        """Get message by id"""
        user_urn = g.user_urn
        # check user is authorised to view message
        message_service = Retriever()
        resp = message_service.retrieve_message(message_id, user_urn)
        return jsonify(resp)


class MessageModifyById(Resource):
    """Update message status by id"""

    @staticmethod
    def put(message_id):
        """Update message by status"""
        user_urn = g.user_urn

        request_data = request.get_json()

        action, label = MessageModifyById.validate_request(request_data)

        message = Retriever().retrieve_message(message_id, user_urn)

        if label == Labels.UNREAD.value:
            resp = MessageModifyById.modify_unread(action, message, user_urn)
        else:
            resp = MessageModifyById.modify_label(action, message, user_urn, label)

        if resp:
            res = jsonify({'status': 'ok'})
            res.status_code = 200

        else:
            res = jsonify({'status': 'error'})
            res.status_code = 400
        return res

    @staticmethod
    def modify_label(action, message, user_urn, label):
        """Adds or deletes a label"""
        label_exists = label in message
        if action == 'add' and not label_exists:
            return Modifier.add_label(label, message, user_urn)
        if label_exists:
            return Modifier.remove_label(label, message, user_urn)
        else:
            return False

    @staticmethod
    def modify_unread(action, message, user_urn):
        if action == 'add':
            return Modifier.add_unread(message, user_urn)
        return Modifier.del_unread(message, user_urn)

    @staticmethod
    def validate_request(request_data):
        """Used to validate data within request body for ModifyById"""
        if 'label' not in request_data:
            raise BadRequest(description="No label provided")

        label = request_data["label"]
        if label not in Labels.label_list.value:
            raise BadRequest(description="Invalid label provided: {0}".format(label))

        if label not in [Labels.ARCHIVE.value, Labels.UNREAD.value]:
            raise BadRequest(description="Non modifiable label provided: {0}".format(label))

        if 'action' not in request_data:
            raise BadRequest(description="No action provided")

        action = request_data["action"]
        if action not in ["add", "remove"]:
            raise BadRequest(description="Invalid action requested: {0}".format(action))

        return action, label
