
import logging

from flask import g, request
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
        string_query_args, page, limit, _, _1, _2, _3, _4, _5 = get_options(request.args)  # NOQA TODO - Named Tuple
        message_service = Retriever()
        status, conversation = message_service.retrieve_thread(thread_id, g.user, page, limit)

        if status:
            resp = paginated_list_to_json(conversation, page, limit, request.host_url, g.user, string_query_args,
                                          THREAD_BY_ID_ENDPOINT + "/" + thread_id)
            resp.status_code = 200
            return resp


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""

        string_query_args, page, limit, _, _1, _2, _3, _4, _5 = get_options(request.args)

        message_service = Retriever()
        status, result = message_service.retrieve_thread_list(page, limit, g.user)

        if status:
            resp = paginated_list_to_json(result, page, limit, request.host_url,
                                          g.user, string_query_args, THREAD_LIST_ENDPOINT)
            resp.status_code = 200
            return resp
