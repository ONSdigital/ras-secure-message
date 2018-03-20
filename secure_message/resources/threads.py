
import logging

from flask import g, make_response, request
from flask_restful import Resource
from structlog import wrap_logger
from secure_message.common.utilities import get_options, paginated_list_to_json
from secure_message.constants import THREAD_LIST_ENDPOINT, THREAD_BY_ID_ENDPOINT
from secure_message.repository.retriever import Retriever

logger = wrap_logger(logging.getLogger(__name__))


class ThreadById(Resource):
    """Return list of messages in a thread for user"""

    @staticmethod
    def get(thread_id):
        """Get messages by thread id"""
        logger.info("Getting messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        message_args = get_options(request.args)  # NOQA TODO - Named Tuple

        conversation = Retriever().retrieve_thread(thread_id, g.user, message_args)

        logger.info("Successfully retrieved messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        return make_response(paginated_list_to_json(conversation,
                                                    request.host_url,
                                                    g.user,
                                                    message_args,
                                                    THREAD_BY_ID_ENDPOINT + "/" + thread_id,
                                                    body_summary=False), 200)


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""
        logger.info("Getting list of threads for user", user_uuid=g.user.user_uuid)
        message_args = get_options(request.args)

        result = Retriever().retrieve_thread_list(g.user, message_args)

        logger.info("Successfully retrieved threads for user", user_uuid=g.user.user_uuid)
        return make_response(paginated_list_to_json(result, request.host_url, g.user, message_args, THREAD_LIST_ENDPOINT), 200)
