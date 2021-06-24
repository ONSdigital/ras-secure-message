import logging

from flask import abort, request, jsonify, g, current_app, make_response
from flask_restful import Resource
from marshmallow import ValidationError
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest

from secure_message import constants
from secure_message.common.alerts import AlertViaGovNotify, AlertViaLogging
from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.database import SecureMessage
from secure_message.repository.modifier import Modifier
from secure_message.repository.retriever import Retriever
from secure_message.repository.saver import Saver
from secure_message.services.service_toggles import party, internal_user_service
from secure_message.validation.domain import MessageSchema, MessagePatch, Message

logger = wrap_logger(logging.getLogger(__name__))


"""Rest endpoint for message resources."""


class MessageSend(Resource):
    """Send message for a user"""

    def post(self):
        """used to handle POST requests to send a message"""
        logger.info("Message send POST request.")
        if request.headers.get('Content-Type', '').lower() != 'application/json':
            # API only returns JSON
            logger.info('Request must set accept content type "application/json" in header.')
        post_data = request.get_json(force=True)

        post_data['from_internal'] = g.user.is_internal
        message = self._validate_post_data(post_data)

        has_survey_category = False if 'category' in post_data and post_data['category'] in ['TECHNICAL', 'MISC'] else \
            True
        # Validate claim
        if not self._has_valid_claim(g.user, message) and has_survey_category:
            logger.info("Message send failed", error="Invalid claim")
            return make_response(jsonify("Invalid claim"), 403)

        logger.info("Message passed validation")
        self._message_save(message)
        # listener errors are logged but still a 201 reported
        MessageSend._alert_listeners(message)
        return make_response(jsonify({'status': '201',
                                      'msg_id': message.msg_id,
                                      'thread_id': message.thread_id}), 201)

    @staticmethod
    def _has_valid_claim(user, message: Message) -> bool:
        """Validates that the user has a valid claim to interact with the business and survey in the post data
        internal users have claims to everything, respondents need to check against party"""
        return user.is_internal or party.does_user_have_claim(user.user_uuid, message.business_id, message.survey_id)

    @staticmethod
    def _message_save(message: Message):
        """Saves the message to the database along with the subsequent status and audit"""
        Saver.save_message(message)
        Saver.save_msg_event(message.msg_id, EventsApi.SENT.value)

        Saver.save_msg_status(message.msg_from, message.msg_id, Labels.SENT.value)
        Saver.save_msg_status(message.msg_to[0], message.msg_id, Labels.INBOX.value)
        Saver.save_msg_status(message.msg_to[0], message.msg_id, Labels.UNREAD.value)

    @staticmethod
    def _validate_post_data(post_data: dict) -> Message:
        if 'msg_id' in post_data:
            raise BadRequest(description="Message can not include msg_id")

        try:
            message = MessageSchema().load(post_data)
        except ValidationError as e:
            logger.info('Message send failed', errors=e.messages)
            raise BadRequest(e.messages)

        if post_data.get('thread_id'):
            conversation_metadata = Retriever.retrieve_conversation_metadata(post_data.get('thread_id'))
            # Ideally, we'd return a 404 if there isn't a record in the conversation table.  But until we
            # ensure there is a record in here for every thread_id in the secure_message table, we just have to
            # assume that it's fine if it's empty.
            if conversation_metadata and conversation_metadata.is_closed:
                raise BadRequest(description="Cannot reply to a closed conversation")
        return message

    @staticmethod
    def _alert_listeners(message):
        """used to alert user once messages have been saved"""
        try:
            MessageSend._try_send_alert_email(message)
        except Exception as e:
            logger.error('Uncaught exception in Message.alert_listeners', exception=e)

    @staticmethod
    def _try_send_alert_email(message):
        """Send an email to recipient if appropriate"""
        party_data = None
        if g.user.is_internal:
            party_data = party.get_user_details(message.msg_to[0])  # NOQA TODO avoid 2 lookups (see validate)
            if party_data:
                if 'emailAddress' in party_data[0] and party_data[0]['emailAddress'].strip():
                    recipient_email = party_data[0]['emailAddress'].strip()
                    alert_method = AlertViaLogging() if current_app.config['NOTIFY_VIA_GOV_NOTIFY'] == '0' else \
                        AlertViaGovNotify(current_app.config)
                    personalisation = MessageSend._create_message_url(message.thread_id)
                    alert_method.send(recipient_email, message.msg_id, personalisation, message.survey_id,
                                      party_data[0]['id'])
                else:
                    logger.error('User does not have an emailAddress specified', msg_to=message.msg_to[0])
            # else not testable as fails validation
        return party_data

    @staticmethod
    def _create_message_url(thread_id):
        url = f'{current_app.config["FRONTSTAGE_URL"]}/secure-message/threads/{thread_id}#latest-message'
        return {"MESSAGE_URL": url}

    @staticmethod
    def _get_user_name(user, message):
        user_name = 'Unknown user'
        is_internal_user = user.is_internal
        user_data = internal_user_service.get_user_details(message.msg_from) if is_internal_user else party. \
            get_user_details(message.msg_from)

        if user_data:
            first_name = user_data.get('firstName', '') if is_internal_user else user_data[0].get('firstName', '')
            last_name = user_data.get('lastName', '') if is_internal_user else user_data[0].get('lastName', '')
            full_name = f'{first_name} {last_name}'.strip()
            if full_name:
                user_name = full_name

        return user_name


class MessageById(Resource):

    def patch(self, message_id: str):
        """Patch message data"""
        bound_logger = logger.bind(message_id=message_id, user_uuid=g.user.user_uuid)
        bound_logger.info("Validating request")
        if not g.user.is_internal:
            bound_logger.info("Message modification is forbidden")
            abort(403)
        if request.headers.get('Content-Type', '').lower() != 'application/json':
            bound_logger.info('Request must set accept content type "application/json" in header.')
            raise BadRequest(description='Request must set accept content type "application/json" in header.')

        bound_logger.info("Retrieving metadata for thread")
        request_data = request.get_json()
        message = Retriever.retrieve_populated_message_object(message_id)
        if message is None:
            abort(404)
        self._validate_patch_request(request_data, message)

        bound_logger.info("Attempting to modify data for message")
        Modifier.patch_message(request_data, message)

        bound_logger.info("Message data update successful")
        bound_logger.unbind('message_id', 'user_uuid')
        return '', 204

    @staticmethod
    def _validate_patch_request(request_data: dict, message: SecureMessage):
        """Used to validate data within request body"""
        bound_logger = logger.bind(message_id=message.msg_id, user_uuid=g.user.user_uuid)
        # Check if it's empty
        if not request_data:
            bound_logger.info('No properties provided')
            raise BadRequest(description="No properties provided")

        try:
            MessagePatch().load(request_data)
        except ValidationError as e:
            bound_logger.error("Errors found when validating request data", errors=e.messages)
            raise BadRequest(e.messages)


class MessageModifyById(Resource):
    """Update message status by id"""

    @staticmethod
    def put(message_id):
        """Update message by status"""

        request_data = request.get_json()
        action, label = MessageModifyById._validate_request(request_data)
        message = Retriever.retrieve_message(message_id, g.user)

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
        if message['msg_to'][0] != user.user_uuid and message['msg_to'][0] != constants.NON_SPECIFIC_INTERNAL_USER:
            return False
        if action == 'add':
            return Modifier.add_unread(message, user)
        return Modifier.mark_message_as_read(message, user)

    @staticmethod
    def _validate_request(request_data):
        """Used to validate data within request body for ModifyById"""
        if 'label' not in request_data:
            logger.info('No label provided')
            raise BadRequest(description="No label provided")

        label = request_data["label"]
        if label not in Labels.label_list.value:
            logger.info('Invalid label provided', label=label)
            raise BadRequest(description=f"Invalid label provided: {label}")

        if label != Labels.UNREAD.value:
            logger.info('Non modifiable label provided', label=label)
            raise BadRequest(description=f"Non modifiable label provided: {label}")

        if 'action' not in request_data:
            logger.info('No action provided')
            raise BadRequest(description="No action provided")

        action = request_data["action"]
        if action not in ["add", "remove"]:
            logger.info('Invalid action requested', action=action)
            raise BadRequest(description=f"Invalid action requested: {action}")

        return action, label
