from distutils.util import strtobool
import logging

from flask import abort, g, jsonify, request
from flask_restful import Resource
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest

from secure_message.common.utilities import get_options, process_paginated_list, add_users_and_business_details
from secure_message.constants import THREAD_LIST_ENDPOINT
from secure_message.repository.modifier import Modifier
from secure_message.repository.retriever import Retriever

logger = wrap_logger(logging.getLogger(__name__))


class ThreadById(Resource):
    """Return list of messages in a thread for user"""

    @staticmethod
    def get(thread_id):
        """Get messages by thread id"""
        logger.info("Getting messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)

        conversation = Retriever().retrieve_thread(thread_id, g.user)
        conversation_metadata = Retriever().retrieve_thread_metadata(thread_id)

        logger.info("Successfully retrieved messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        messages = []
        for message in conversation.all():
            msg = message.serialize(g.user, body_summary=False)
            messages.append(msg)

        if conversation_metadata.is_closed:
            return jsonify({"messages": add_users_and_business_details(messages),
                            "metadata": ThreadById._build_metadata(conversation_metadata)})
        else:
            return jsonify({"messages": add_users_and_business_details(messages)})

    @staticmethod
    def _build_metadata(conversation_metadata):
        return {
            "is_closed": conversation_metadata.is_closed,
            "closed_by": conversation_metadata.closed_by,
            "closed_by_uuid": conversation_metadata.closed_by_uuid,
            "closed_on": conversation_metadata.closed_on
        }

    @staticmethod
    def patch(thread_id):
        """Modify conversation metadata"""

        logger.info("Attempting to modify metadata for thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        request_data = request.form
        msg_property, value = ThreadById._validate_request(request_data)

        logger.info("Getting metadata for thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        metadata = Retriever.retrieve_thread_metadata(thread_id)
        if msg_property == 'is_closed':
            if value:
                if metadata.is_closed:
                    logger.info("Conversation already closed", thread_id=thread_id, user_uuid=g.user.user_uuid)
                    raise BadRequest(description="Conversation already closed")
                logger.info("About to close conversation")
                Modifier.add_closed_status_to_conversation(metadata, g.user)
            else:
                logger.info("About re-open conversation", thread_id=thread_id, user_uuid=g.user.user_uuid)
                Modifier.remove_closed_status_from_conversation(metadata, g.user)

        logger.info("Thread metadata update successful", thread_id=thread_id, user_uuid=g.user.user_uuid)
        return '', 204

    @staticmethod
    def _validate_request(request_data):
        """Used to validate data within request body for ModifyById"""
        if not g.user.is_internal:
            logger.info("Thread modification is forbidden")
            abort(403)
        # Check if it's empty
        if not request_data:
            logger.error('No properties provided')
            raise BadRequest(description="No properties provided")
        if request_data['is_closed'] not in ['True', 'False']:
            logger.error('Invalid value provided')
            raise BadRequest(description="Invalid label provided")

        return 'is_closed', strtobool(request_data['is_closed'])


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""
        logger.info("Getting list of threads for user", user_uuid=g.user.user_uuid)
        message_args = get_options(request.args)
        result = Retriever().retrieve_thread_list(g.user, message_args)

        logger.info("Successfully retrieved threads for user", user_uuid=g.user.user_uuid)
        messages, links = process_paginated_list(result, request.host_url, g.user, message_args, THREAD_LIST_ENDPOINT)
        messages = add_users_and_business_details(messages)
        return jsonify({"messages": messages, "_links": links})
