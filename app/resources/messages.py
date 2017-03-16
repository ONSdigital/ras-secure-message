from flask_restful import Resource, abort
from flask import request
from flask import jsonify
from app.domain_model.domain import Message
from app.services.saver import Saver

"""Rest endpoint for message resources. Messages are immutable, they can only be created and archived."""

class MessageList(Resource):

    """Return a list of messages for the user"""
    def get(self):
        resp = jsonify({'status': "ok"})
        resp.status_code = 200
        return resp


class MessageSend(Resource):

    """Send message for a user"""
    def post(self):
        message_json = request.get_json()
        message = Message(message_json['to'], message_json['from'], message_json['body'])
        message_service = Saver()
        message_service.saveMessage(message)
        resp = jsonify({'status': "ok"})
        resp.status_code = 200
        return resp


class MessageById(Resource):

    """Get message by id"""
    def get(self, id):
        resp = jsonify({'status': "ok"})
        resp.status_code = 200
        return resp

    """Update message by id"""
    def put(self):
        resp = jsonify({'status': "ok"})
        resp.status_code = 200
        return resp
