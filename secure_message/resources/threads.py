import logging

from flask import g, jsonify, make_response, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest

from secure_message.common.utilities import (
    add_users_and_business_details,
    get_options,
    process_paginated_list,
)
from secure_message.constants import THREAD_LIST_ENDPOINT
from secure_message.repository.modifier import Modifier
from secure_message.repository.retriever import Retriever
from secure_message.validation.thread import ThreadPatch

logger = wrap_logger(logging.getLogger(__name__))


class ThreadById(Resource):
    """Return list of messages in a thread for user"""

    @staticmethod
    def get(thread_id):
        """Get messages by thread id"""
        logger.info("Getting messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)

        try:
            conversation = Retriever.retrieve_thread(thread_id, g.user)
            conversation_metadata = Retriever.retrieve_conversation_metadata(thread_id)
        except SQLAlchemyError:
            return make_response(
                jsonify({"message": "Database error while retrieving message thread", "thread_id": thread_id}), 500
            )

        logger.info("Successfully retrieved messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        messages = []
        for message in conversation:
            msg = message.serialize(g.user, body_summary=False)
            messages.append(msg)

        closed_at = None if conversation_metadata.closed_at is None else conversation_metadata.closed_at.isoformat()

        return jsonify(
            {
                "messages": add_users_and_business_details(messages),
                "is_closed": conversation_metadata.is_closed,
                "closed_by": conversation_metadata.closed_by,
                "closed_by_uuid": conversation_metadata.closed_by_uuid,
                "closed_at": closed_at,
                "category": conversation_metadata.category,
            }
        )

    @staticmethod
    def patch(thread_id):
        """Modify conversation metadata"""
        bound_logger = logger.bind(thread_id=thread_id, user_uuid=g.user.user_uuid)
        bound_logger.info("Validating request")

        if not g.user.is_internal:
            bound_logger.info("Thread modification is forbidden")
            return make_response(
                jsonify({"title": "Error when modifying thread", "message": "Thread modification is forbidden"}), 403
            )

        if request.headers.get("Content-Type", "").lower() != "application/json":
            bound_logger.info('Request must set accept content type "application/json" in header.')
            raise BadRequest(description='Request must set accept content type "application/json" in header.')

        bound_logger.info("Retrieving metadata for thread")
        request_data = request.get_json()
        try:
            conversation = Retriever.retrieve_conversation_metadata(thread_id)

            if conversation is None:
                return make_response(
                    jsonify({"title": "Error when modifying thread", "message": "Thread not found"}), 404
                )
            ThreadById._validate_patch_request(request_data, conversation)

            bound_logger.info("Attempting to modify metadata for thread")
            Modifier.patch_conversation(request_data, conversation)

            if request_data.get("is_closed") is not None:
                if request_data.get("is_closed"):
                    bound_logger.info("About to close conversation")
                    Modifier.close_conversation(conversation, g.user)
                else:
                    bound_logger.info("About to re-open conversation")
                    Modifier.open_conversation(conversation, g.user)
            else:  # If anything changes in a thread that isn't is_closed, mark as unread
                bound_logger.info("Marking thread as unread after thread data change")
                full_conversation = Retriever.retrieve_thread(thread_id, g.user)

                # First message in the list is always the most recent due to retrieve_thread ordering by id
                most_recent_message = full_conversation[0].serialize(g.user)

                # We only want to mark messages as unread if the most recent message was from a respondent.  Otherwise,
                # we're marking our own message as unread which is a bit pointless.
                if not most_recent_message["from_internal"]:
                    if "INBOX" in most_recent_message["labels"]:
                        if "UNREAD" not in most_recent_message["labels"]:
                            Modifier.add_unread(most_recent_message, g.user)
                            Modifier.patch_message({"read_at": None}, full_conversation[0])
        except SQLAlchemyError as e:
            return make_response(
                jsonify({"title": "Database error when modifying thread", "detail": e.__class__.__name__}), 500
            )

        bound_logger.info("Thread metadata update successful")
        bound_logger.unbind("thread_id", "user_uuid")
        return "", 204

    @staticmethod
    def _validate_patch_request(request_data, metadata):
        """Used to validate data within request body"""
        bound_logger = logger.bind(thread_id=metadata.id, user_uuid=g.user.user_uuid)
        # Check if it's empty
        if not request_data:
            bound_logger.info("No properties provided")
            raise BadRequest(description="No properties provided")

        try:
            ThreadPatch().load(request_data)
        except ValidationError as e:
            bound_logger.error("Errors found when validating request data", errors=e.messages)
            raise BadRequest(e.messages)

        # Perform extra validation that marshmallow cannot handle
        if "is_closed" in request_data:
            if metadata.is_closed and request_data["is_closed"] is True:
                bound_logger.info("Conversation already closed")
                raise BadRequest(description="Conversation already closed")
            if not metadata.is_closed and request_data["is_closed"] is False:
                bound_logger.info("Conversation already open")
                raise BadRequest(description="Conversation already open")

        bound_logger.info("Thread validation successful")
        bound_logger.unbind("thread_id", "user_uuid")


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""
        logger.info("Getting list of threads for user", user_uuid=g.user.user_uuid)
        message_args = get_options(request.args)

        ThreadList._validate_request(message_args, g.user)

        try:
            result = Retriever.retrieve_thread_list(g.user, message_args)
        except SQLAlchemyError as e:
            return make_response(
                jsonify({"title": "Database error when getting thread list", "detail": e.__class__.__name__}), 500
            )

        logger.info("Successfully retrieved threads for user", user_uuid=g.user.user_uuid)
        messages, links = process_paginated_list(result, request.host_url, g.user, message_args, THREAD_LIST_ENDPOINT)
        if messages:
            messages = add_users_and_business_details(messages)
        return jsonify({"messages": messages, "_links": links})

    @staticmethod
    def _validate_request(request_args, user):
        if request_args.my_conversations and user.is_respondent:
            logger.info("My conversations option not available to respondents", user_uuid=user.user_uuid)
            raise BadRequest(description="My conversations option not available to respondents")

        if request_args.new_respondent_conversations and user.is_respondent:
            logger.info("New respondent conversation option not available to respondents", user_uuid=user.user_uuid)
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

        try:
            if message_args.all_conversation_types:
                logger.info("Getting counts for all conversation states for user", user_uuid=g.user.user_uuid)
                return jsonify(totals=Retriever.thread_count_by_survey_and_conversation_states(message_args, g.user))

            if message_args.unread_conversations:
                logger.info("Getting counts of unread conversations", user_uuid=g.user.user_uuid)
                return jsonify(total=Retriever.unread_message_count(g.user))

            return jsonify(total=Retriever.thread_count_by_survey(message_args, g.user))
        except SQLAlchemyError as e:
            return make_response(
                jsonify({"title": "Database error when getting thread counts", "detail": e.__class__.__name__}), 500
            )
