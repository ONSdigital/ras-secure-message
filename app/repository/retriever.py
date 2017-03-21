from app.data_model.database import Message
from flask import jsonify


class Retriever:

    @staticmethod
    def retrieve_message_list():
        db_model = Message()
        result = db_model.query.limit(15).all()
        return jsonify([i.serialize for i in result])
