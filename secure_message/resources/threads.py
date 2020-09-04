import logging

from werkzeug.exceptions import BadRequest
from flask import abort, g, jsonify, request
from flask_restful import Resource
from structlog import wrap_logger

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

        conversation = Retriever.retrieve_thread(thread_id, g.user)
        conversation_metadata = Retriever.retrieve_conversation_metadata(thread_id)

        logger.info("Successfully retrieved messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        messages = []
        for message in conversation.all():
            msg = message.serialize(g.user, body_summary=False)
            messages.append(msg)

        if conversation_metadata and conversation_metadata.is_closed:
            return jsonify({"messages": add_users_and_business_details(messages),
                            "is_closed": conversation_metadata.is_closed,
                            "closed_by": conversation_metadata.closed_by,
                            "closed_by_uuid": conversation_metadata.closed_by_uuid,
                            "closed_at": conversation_metadata.closed_at.isoformat()})

        return jsonify({"messages": add_users_and_business_details(messages),
                        "is_closed": False})

    @staticmethod
    def patch(thread_id):
        """Modify conversation metadata"""
        bound_logger = logger.bind(thread_id=thread_id, user_uuid=g.user.user_uuid)
        bound_logger.info("Validating request")
        if not g.user.is_internal:
            bound_logger.info("Thread modification is forbidden")
            abort(403)
        if request.headers.get('Content-Type', '').lower() != 'application/json':
            bound_logger.info('Request must set accept content type "application/json" in header.')
            raise BadRequest(description='Request must set accept content type "application/json" in header.')

        bound_logger.info("Retrieving metadata for thread")
        request_data = request.get_json()
        metadata = Retriever.retrieve_conversation_metadata(thread_id)
        if metadata is None:
            abort(404)
        ThreadById._validate_request(request_data, metadata)

        bound_logger.info("Attempting to modify metadata for thread")
        if request_data.get('is_closed'):
            bound_logger.info("About to close conversation")
            Modifier.close_conversation(metadata, g.user)
        else:
            bound_logger.info("About to re-open conversation")
            Modifier.open_conversation(metadata, g.user)

        bound_logger.info("Thread metadata update successful")
        bound_logger.unbind('thread_id', 'user_uuid')
        return '', 204

    @staticmethod
    def _validate_request(request_data, metadata):
        """Used to validate data within request body"""
        bound_logger = logger.bind(thread_id=metadata.id, user_uuid=g.user.user_uuid)
        # Check if it's empty
        if not request_data:
            bound_logger.info('No properties provided')
            raise BadRequest(description="No properties provided")
        if 'is_closed' not in request_data:
            bound_logger.info('Invalid properties provided')
            raise BadRequest(description="Only 'is_closed' property may be provided")
        if not isinstance(request_data['is_closed'], bool):
            bound_logger.info('Invalid value provided')
            raise BadRequest(description="Invalid value provided")
        if metadata.is_closed and request_data['is_closed'] is True:
            bound_logger.info("Conversation already closed")
            raise BadRequest(description="Conversation already closed")
        if not metadata.is_closed and request_data['is_closed'] is False:
            bound_logger.info("Conversation already open")
            raise BadRequest(description="Conversation already open")

        bound_logger.info("Thread validation successful")
        bound_logger.unbind('thread_id', 'user_uuid')


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""
        logger.info("Getting list of threads for user", user_uuid=g.user.user_uuid)
        message_args = get_options(request.args)

        ThreadList._validate_request(message_args, g.user)

        result = Retriever.retrieve_thread_list(g.user, message_args)

        logger.info("Successfully retrieved threads for user", user_uuid=g.user.user_uuid)
        messages, links = process_paginated_list(result, request.host_url, g.user, message_args, THREAD_LIST_ENDPOINT)
        if messages:
            messages = add_users_and_business_details(messages)
        return jsonify({"messages": messages, "_links": links})

    @staticmethod
    def _validate_request(request_args, user):
        if request_args.my_conversations and user.is_respondent:
            logger.info('My conversations option not available to respondents', user_uuid=user.user_uuid)
            raise BadRequest(description="My conversations option not available to respondents")

        if request_args.new_respondent_conversations and user.is_respondent:
            logger.info('New respondent conversation option not available to respondents', user_uuid=user.user_uuid)
            raise BadRequest(description="New respondent conversation option not available to respondents")


class ThreadCounter(Resource):

    @staticmethod
    def get():
        """Get count of all conversations for a specific internal user
        Typically for a specific survey, supports filtering by case, collection exercise, business party id etc

        :returns: if all_conversation_types is set 'true' returns json representing all 4 counts
                  else returns the count for the single type combination requested.
        """
        logger.info("Getting count of threads for user", user_uuid=g.user.user_uuid)
        message_args = get_options(request.args)

        if message_args.all_conversation_types:
            logger.info("Getting counts for all conversation states for user", user_uuid=g.user.user_uuid)
            return jsonify(totals=Retriever.thread_count_by_survey_and_conversation_states(message_args, g.user))

        if message_args.unread_conversations:
            logger.info("Getting counts of unread conversations", user_uuid=g.user.user_uuid)
            return jsonify(total=Retriever.unread_message_count(g.user))

        return jsonify(total=Retriever.thread_count_by_survey(message_args, g.user))
