import logging
from flask import request, jsonify, g, Response
from flask_restful import Resource
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest
from app import settings
from app.common.alerts import AlertUser
from app.common.labels import Labels
from app.common.utilities import get_options, paginated_list_to_json, \
    add_business_details, add_to_and_from_details,add_users_and_business_details
from app.constants import MESSAGE_LIST_ENDPOINT
from app.repository.modifier import Modifier
from app.repository.retriever import Retriever
from app.repository.saver import Saver
from app.resources.drafts import DraftModifyById
from app.validation.domain import MessageSchema
from app.authorization.authorizer import Authorizer
from app.services.service_toggles import party, case_service
from app import constants


logger = wrap_logger(logging.getLogger(__name__))


"""Rest endpoint for message resources. Messages are immutable, they can only be created."""


class MessageList(Resource):
    """Return a list of messages for the user"""

    @staticmethod
    def get():
        """Get message list with options"""

        string_query_args, page, limit, ru_id, survey, cc, label, desc, ce = get_options(request.args)

        message_service = Retriever()
        status, result = message_service.retrieve_message_list(page, limit, g.user,
                                                               ru_id=ru_id, survey=survey, cc=cc, label=label, descend=desc, ce=ce)

        if status:
            resp = paginated_list_to_json(result, page, limit, request.host_url,
                                          g.user, string_query_args, MESSAGE_LIST_ENDPOINT)
            resp.status_code = 200
            return resp


class MessageSend(Resource):
    """Send message for a user"""

    def post(self):
        """used to handle POST requests to send a message"""
        logger.info("Message send POST request.")
        post_data = request.get_json()
        is_draft = False

        draft_id = None
        if 'msg_id' in post_data:
            is_draft, returned_draft = Retriever().check_msg_id_is_a_draft(post_data['msg_id'], g.user)
            if is_draft is True:
                draft_id = post_data['msg_id']
                post_data['msg_id'] = ''

                if post_data['thread_id'] == draft_id:
                    post_data['thread_id'] = ''

            else:
                raise BadRequest(description="Message can not include msg_id")

            last_modified = DraftModifyById.etag_check(request.headers, returned_draft)
            if last_modified is False:

                res = Response(response="Draft has been modified since last check", status=409,
                               mimetype="text/html")
                return res

        message = MessageSchema().load(post_data)
        if message.errors == {}:
            return self._message_save(message, is_draft, draft_id)
        else:
            resp = jsonify(message.errors)
            resp.status_code = 400
            return resp

    def _message_save(self, message, is_draft, draft_id):
        """Saves the message to the database along with the subsequent status and audit"""
        save = Saver()
        save.save_message(message.data)
        save.save_msg_event(message.data.msg_id, 'Sent')
        if g.user.is_respondent:
            save.save_msg_status(message.data.msg_from, message.data.msg_id, Labels.SENT.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.UNREAD.value)
        else:
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.SENT.value)
            save.save_msg_audit(message.data.msg_id, message.data.msg_from)
            save.save_msg_status(message.data.msg_to[0], message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.msg_to[0], message.data.msg_id, Labels.UNREAD.value)

        if is_draft is True:
            Modifier().del_draft(draft_id)

        # listener errors are logged but still a 201 reported
        MessageSend._alert_listeners(message.data)

        resp = jsonify({'status': '201', 'msg_id': message.data.msg_id, 'thread_id': message.data.thread_id})
        resp.status_code = 201
        return resp

    @staticmethod
    def _alert_listeners(message):
        """used to alert user and case service once messages have been saved"""
        try:
            MessageSend._try_send_alert_email(message)
            MessageSend._inform_case_service(message)
        except Exception as e:
            logger.error('Uncaught exception in Message.alert_listeners: {}'.format(e))

    @staticmethod
    def _try_send_alert_email(message):
        """Send an email to recipient if appropriate"""
        party_data=None
        if message.msg_to[0] != constants.BRES_USER:
            party_data, status_code = party.get_user_details(message.msg_to[0])  # todo avoid 2 lookups (see validate)
            if status_code == 200:
                if 'emailAddress' in party_data and len(party_data['emailAddress'].strip()) > 0:
                    recipient_email = party_data['emailAddress'].strip()
                    alert_user = AlertUser()
                    alert_user.send(recipient_email, message.msg_id)
                else:
                    logger.error('UserId {0} does not have an emailAddress specified'.format(message.msg_to[0]))
            else:
                logger.error('UserId {0} not known in party service : alert email not sent but message stored'.format(message.msg_to[0]))
        return party_data

    @staticmethod
    def _inform_case_service(message):
        if message.msg_from == constants.BRES_USER:
            case_user = constants.BRES_USER
        else:
            party_data, status_code = party.get_user_details(message.msg_from)  # todo avoid 2 lookups (see validate)
            if status_code == 200:
                first_name = party_data['firstName'] if party_data['firstName'] is not None else ''
                last_name = party_data['lastName'] if party_data['lastName'] is not None else ''
                case_user = '{} {}'.format(first_name, last_name).strip()
                if len(case_user) == 0:
                    case_user = 'Unknown user'
                    logger.info('no user names in party data for id {0} Unknown user used in case '.format(party_data['id']))
            else:
                logger.info('could not retrieve {} details from party using Unknown user for case'.format(message.msg_from))
                case_user = 'Unknown user'
        case_service.store_case_event(message.collection_case, case_user)



class MessageById(Resource):
    """Get and update message by id"""

    @staticmethod
    def get(message_id):
        """Get message by id"""
        # check user is authorised to view message
        message_service = Retriever()
        message = message_service.retrieve_message(message_id, g.user)

        message = add_users_and_business_details([message])[0]
        if Authorizer().can_user_view_message(g.user, message):
            return jsonify(message)
        else:
            result = jsonify({'status': 'error'})
            result.status_code = 403
            return result

class MessageModifyById(Resource):
    """Update message status by id"""

    @staticmethod
    def put(message_id):
        """Update message by status"""

        request_data = request.get_json()
        action, label = MessageModifyById._validate_request(request_data)
        message = Retriever().retrieve_message(message_id, g.user)

        if label == Labels.UNREAD.value:
            resp = MessageModifyById._try_modify_unread(action, message, g.user)
        else:
            resp = MessageModifyById._modify_label(action, message, g.user, label)

        if resp:
            res = jsonify({'status': 'ok'})
            res.status_code = 200

        else:
            res = jsonify({'status': 'error'})
            res.status_code = 400
        return res

    @staticmethod
    def _modify_label(action, message, user, label):
        """Adds or deletes a label"""
        label_exists = label in message
        if action == 'add' and not label_exists:
            return Modifier.add_label(label, message, user)
        if label_exists:
            return Modifier.remove_label(label, message, user)
        else:
            return False

    @staticmethod
    def _try_modify_unread(action, message, user):
        """Used to validate that the label can be modified to read"""
        if message['msg_to'][0] != user.user_uuid:
            return False
        if action == 'add':
            return Modifier.add_unread(message, user)
        return Modifier.del_unread(message, user)

    @staticmethod
    def _validate_request(request_data):
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
