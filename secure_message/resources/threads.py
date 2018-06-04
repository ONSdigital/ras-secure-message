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
        conversation_metadata = Retriever.retrieve_conversation_metadata(thread_id)

        logger.info("Successfully retrieved messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        messages = []
        for message in conversation.all():
            msg = message.serialize(g.user, body_summary=False)
            messages.append(msg)

        if conversation_metadata.is_closed:
            return jsonify({"messages": add_users_and_business_details(messages),
                            "is_closed": conversation_metadata.is_closed,
                            "closed_by": conversation_metadata.closed_by,
                            "closed_by_uuid": conversation_metadata.closed_by_uuid,
                            "closed_at": conversation_metadata.closed_at})

        return jsonify({"messages": add_users_and_business_details(messages)})

    @staticmethod
    def patch(thread_id):
        """Modify conversation metadata"""

        logger.info("Getting metadata for thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        if request.headers['Content-Type'].lower() != 'application/json':
            logger.info('Request must set accept content type "application/json" in header.')
            raise BadRequest(description="'application/json' content type in header missing")

        logger.info("Attempting to modify metadata for thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        request_data = request.get_json()
        metadata = Retriever.retrieve_conversation_metadata(thread_id)
        ThreadById._validate_request(request_data, metadata)

        if request_data.get('is_closed'):
            logger.info("About to close conversation")
            Modifier.close_conversation(metadata, g.user)
        elif not request_data.get('is_closed'):
            logger.info("About re-open conversation", thread_id=thread_id, user_uuid=g.user.user_uuid)
            Modifier.open_conversation(metadata, g.user)

        logger.info("Thread metadata update successful", thread_id=thread_id, user_uuid=g.user.user_uuid)
        return '', 204

    @staticmethod
    def _validate_request(request_data, metadata):
        """Used to validate data within request body for ModifyById"""
        if not g.user.is_internal:
            logger.info("Thread modification is forbidden")
            abort(403)
        # Check if it's empty
        if not request_data:
            logger.error('No properties provided')
            raise BadRequest(description="No properties provided")
        if not isinstance(request_data['is_closed'], bool):
            logger.error('Invalid value provided')
            raise BadRequest(description="Invalid label provided")
        if metadata.is_closed and request_data['is_closed'] is True:
            logger.info("Conversation already closed", thread_id=metadata.id, user_uuid=g.user.user_uuid)
            raise BadRequest(description="Conversation already closed")
        if not metadata.is_closed and request_data['is_closed'] is False:
            logger.info("Conversation already closed", thread_id=metadata.id, user_uuid=g.user.user_uuid)
            raise BadRequest(description="Conversation already open")

        return 'is_closed', request_data['is_closed']


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
