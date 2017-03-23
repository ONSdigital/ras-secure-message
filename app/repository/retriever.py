from app.data_model.database import Message
from flask import jsonify


class Retriever:
    """Created when retrieving messages"""
    @staticmethod
    def retrieve_message_list():
        db_model = Message()
        result = db_model.query.limit(15).all()
        return jsonify([i.serialize for i in result])

    @staticmethod
    def retrieve_message(message_id):
        db_model = Message()
        result = db_model.query.filter_by(id=message_id).first_or_404()
        return jsonify(result.serialize)
