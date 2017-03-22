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
    def retrieve_message(id):
        db_model = Message()
        result = db_model.query.filter_by(id=id).first()
        return jsonify(result.serialize)
