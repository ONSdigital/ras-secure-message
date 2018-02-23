
import logging

from flask import g, make_response, request
from flask_restful import Resource
from structlog import wrap_logger
from secure_message.common.utilities import get_options, paginated_list_to_json
from secure_message.constants import THREAD_LIST_ENDPOINT, THREAD_BY_ID_ENDPOINT
from secure_message.repository.retriever import Retriever

logger = wrap_logger(logging.getLogger(__name__))


class ThreadById(Resource):
    """Return list of messages for user"""

    @staticmethod
    def get(thread_id):
        """Get messages by thread id"""
        message_args = get_options(request.args)  # NOQA

        conversation = Retriever().retrieve_thread(thread_id, g.user, message_args.page, message_args.limit)

        return make_response(paginated_list_to_json(conversation, message_args.page, message_args.limit, request.host_url, g.user,
                             message_args.string_query_args, THREAD_BY_ID_ENDPOINT + "/" + thread_id), 200)


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""
        message_args = get_options(request.args)
        result = Retriever().retrieve_thread_list(g.user, message_args)

        return make_response(paginated_list_to_json(result, message_args.page, message_args.limit, request.host_url,
                                                    g.user, message_args.string_query_args, THREAD_LIST_ENDPOINT), 200)
