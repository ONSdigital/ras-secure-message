import logging

from flask import g, jsonify, request
from werkzeug.exceptions import BadRequest
from flask_restful import Resource
from structlog import wrap_logger

from secure_message.common.utilities import get_options, process_paginated_list, add_users_and_business_details
from secure_message.constants import THREAD_LIST_ENDPOINT
from secure_message.repository.retriever import Retriever

logger = wrap_logger(logging.getLogger(__name__))


class ThreadById(Resource):
    """Return list of messages in a thread for user"""

    @staticmethod
    def get(thread_id):
        """Get messages by thread id"""
        logger.info("Getting messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)

        conversation = Retriever().retrieve_thread(thread_id, g.user)

        logger.info("Successfully retrieved messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        messages = []
        for message in conversation.all():
            msg = message.serialize(g.user, body_summary=False)
            messages.append(msg)
        return jsonify({"messages": add_users_and_business_details(messages)})


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


class ThreadCounter(Resource):
    """Get count of unread messages using v2 endpoint"""
    @staticmethod
    def get():
        survey = request.args.getlist('survey')
        if request.args.get('label'):
            label = str(request.args.get('label'))
            if label.lower() == 'unread':
                return jsonify(name=label, total=Retriever().thread_count_by_survey(g.user, survey, label))
            else:
                logger.debug('Invalid label name', name=label, request=request.url)
                raise BadRequest(description="Invalid label")
        else:
            return jsonify(total=Retriever().thread_count_by_survey(g.user, survey))
