import logging

from flask import request, jsonify, g, Response, current_app
from flask_restful import Resource
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest

from secure_message.common.alerts import AlertUser, AlertViaGovNotify, AlertViaLogging
from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.common.utilities import get_options, paginated_list_to_json, add_users_and_business_details
from secure_message.constants import MESSAGE_LIST_ENDPOINT
from secure_message.repository.modifier import Modifier
from secure_message.repository.retriever import Retriever
from secure_message.repository.saver import Saver
from secure_message.resources.drafts import DraftModifyById
from secure_message.validation.domain import MessageSchema
from secure_message.authorization.authorizer import Authorizer
from secure_message.services.service_toggles import party, case_service
from secure_message import constants

logger = wrap_logger(logging.getLogger(__name__))


"""Rest endpoint for message resources. Messages are immutable, they can only be created."""


class MessageList(Resource):
    """Return a list of messages for the user"""

    @staticmethod
    def get():
        """Get message list with options"""

        message_args = get_options(request.args)

        message_service = Retriever()
        status, result = message_service.retrieve_message_list(message_args.page, message_args.limit, g.user,
                                                               ru_id=message_args.ru_id, survey=message_args.survey,
                                                               cc=message_args.cc, label=message_args.label,
                                                               descend=message_args.desc, ce=message_args.ce)

        if status:
            resp = paginated_list_to_json(result, message_args.page, message_args.limit, request.host_url,
                                          g.user, message_args.string_query_args, MESSAGE_LIST_ENDPOINT)
            resp.status_code = 200
            return resp


class MessageSend(Resource):
    """Send message for a user"""

    def post(self):
        """used to handle POST requests to send a message"""
        logger.info("Message send POST request.")
        if request.headers['Content-Type'].lower() != 'application/json':
            # API only returns JSON
            logger.info('Request must set accept content type "application/json" in header.')
        post_data = request.get_json(force=True)

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
                return Response(response="Draft has been modified since last check", status=409, mimetype="text/html")

        message = self._validate_post_data(post_data)
        if message.errors == {}:
            self._message_save(message, is_draft, draft_id)
            if is_draft:
                Modifier().del_draft(draft_id)
            # listener errors are logged but still a 201 reported
            MessageSend._alert_listeners(message.data)
            resp = jsonify({'status': '201', 'msg_id': message.data.msg_id, 'thread_id': message.data.thread_id})
            resp.status_code = 201
            return resp

        resp = jsonify(message.errors)
        resp.status_code = 400
        logger.error('Message send failed', errors=message.errors)
        return resp

    @staticmethod
    def _validate_post_data(post_data):
        message = MessageSchema().load(post_data)
        return message

    @staticmethod
    def _message_save(message, is_draft, draft_id):
        """Saves the message to the database along with the subsequent status and audit"""
        save = Saver()
        save.save_message(message.data)
        save.save_msg_actors(message.data.msg_id, message.data.msg_from, message.data.msg_to[0], g.user.is_internal)
        save.save_msg_event(message.data.msg_id, EventsApi.SENT.value)
        if g.user.is_respondent:
            save.save_msg_status(message.data.msg_from, message.data.msg_id, Labels.SENT.value)
            save.save_msg_status(constants.BRES_USER, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(constants.BRES_USER, message.data.msg_id, Labels.UNREAD.value)
        else:
            save.save_msg_status(constants.BRES_USER, message.data.msg_id, Labels.SENT.value)
            save.save_msg_status(message.data.msg_to[0], message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.msg_to[0], message.data.msg_id, Labels.UNREAD.value)

    @staticmethod
    def _alert_listeners(message):
        """used to alert user and case service once messages have been saved"""
        try:
            MessageSend._try_send_alert_email(message)
            MessageSend._inform_case_service(message)
        except Exception as e:  # NOQA pylint:disable=broad-except
            logger.error('Uncaught exception in Message.alert_listeners', exception=e)

    @staticmethod
    def _try_send_alert_email(message):
        """Send an email to recipient if appropriate"""
        party_data = None
        if g.user.is_internal:
            party_data, status_code = party.get_user_details(message.msg_to[0])  # NOQA TODO avoid 2 lookups (see validate)
            if status_code == 200:
                if 'emailAddress' in party_data and party_data['emailAddress'].strip():
                    recipient_email = party_data['emailAddress'].strip()
                    alert_method = AlertViaLogging() if current_app.config['NOTIFY_VIA_GOV_NOTIFY'] == '0' else AlertViaGovNotify()
                    alert_user = AlertUser(alert_method)
                    alert_user.send(recipient_email, message.msg_id)
                else:
                    logger.error('User does not have an emailAddress specified', msg_to=message.msg_to[0])
            # else not testable as fails validation
        return party_data

    @staticmethod
    def _inform_case_service(message):
        if current_app.config['NOTIFY_CASE_SERVICE'] == '1':
            if message.msg_from == constants.BRES_USER:
                case_user = constants.BRES_USER
            else:
                party_data, status_code = party.get_user_details(message.msg_from)  # NOQA TODO avoid 2 lookups(see validate)
                if status_code == 200:
                    first_name = party_data['firstName'] if 'firstName' in party_data else ''
                    last_name = party_data['lastName'] if 'lastName' in party_data else ''
                    case_user = '{} {}'.format(first_name, last_name).strip()
                    if not case_user:
                        case_user = 'Unknown user'
                        logger.info('no user names in party data for id  Unknown user used in case ',
                                    party_id=party_data['id'])
                # else not testable , as it fails on validation
            case_service.store_case_event(message.collection_case, case_user)
        else:
            logger.info('Case service notifications switched off, hence not sent', msg_id=message.msg_id)


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
        result = jsonify({'status': 'error'})
        result.status_code = 403
        logger.error('Error getting message by ID', msg_id=message_id, status_code=result.status_code)
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
            logger.error('Error updating message', msg_id=message_id, status_code=res.status_code)
        return res

    @staticmethod
    def _modify_label(action, message, user, label):
        """Adds or deletes a label"""
        label_exists = label in message['labels']
        if action == 'add' and not label_exists:
            return Modifier.add_label(label, message, user)
        if label_exists:
            return Modifier.remove_label(label, message, user)
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
            logger.error('No label provided')
            raise BadRequest(description="No label provided")

        label = request_data["label"]
        if label not in Labels.label_list.value:  # NOQA pylint:disable=unsupported-membership-test
            logger.error('Invalid label provided', label=label)
            raise BadRequest(description=f"Invalid label provided: {label}")

        if label not in [Labels.ARCHIVE.value, Labels.UNREAD.value]:
            logger.error('Non modifiable label provided', label=label)
            raise BadRequest(description=f"Non modifiable label provided: {label}")

        if 'action' not in request_data:
            logger.error('No action provided')
            raise BadRequest(description="No action provided")

        action = request_data["action"]
        if action not in ["add", "remove"]:
            logger.error('Invalid action requested', action=action)
            raise BadRequest(description=f"Invalid action requested: {action}")

        return action, label


class MessageCounter(Resource):
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
            raise BadRequest(description='No Label Name Parameter specified.')
