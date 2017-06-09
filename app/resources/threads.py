from flask import g, request
from flask import jsonify
from flask_restful import Resource
from structlog import wrap_logger
import logging
from app.common.utilities import get_options, paginated_list_to_json
from app.constants import THREAD_LIST_ENDPOINT
from app.repository.retriever import Retriever


logger = wrap_logger(logging.getLogger(__name__))

class ThreadById(Resource):
    """Return list of messages for user"""

    @staticmethod
    def get(thread_id):
        """Get messages by thread id"""
        user_urn = g.user_urn
        # check user is authorised to view message
        message_service = Retriever()
        conversation = message_service.retrieve_thread(thread_id, user_urn)
        resp = jsonify(conversation)

        return resp


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""
        string_query_args, page, limit, ru, survey, cc, label, business, desc = get_options(request.args)

        message_service = Retriever()
        status, result = message_service.retrieve_thread_list(page, limit, g.user_urn)

        if status:
            resp = paginated_list_to_json(result, page, limit, request.host_url,
                                                       g.user_urn, string_query_args, THREAD_LIST_ENDPOINT)
            resp.status_code = 200
            return resp
