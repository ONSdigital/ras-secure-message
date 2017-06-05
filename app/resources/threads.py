from flask import g
from flask import jsonify
from flask_restful import Resource
from app.repository.retriever import Retriever


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
