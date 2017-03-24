from app.data_model.database import DbMessage
from flask import jsonify


class Retriever:
    """Created when retrieving messages"""
    @staticmethod
    def retrieve_message_list():
        db_model = DbMessage()
        result = db_model.query.limit(15).all()
        return jsonify([i.serialize for i in result])

    @staticmethod
    def retrieve_message(message_id):
        db_model = DbMessage()
        result = db_model.query.filter_by(id=message_id).first_or_404()
        return jsonify(result.serialize)

    @staticmethod
    def check_db_connection():
        database_status = {"status": "healthy", "errors": "none"}
        resp = jsonify(database_status)
        resp.status_code = 200

        try:
            DbMessage().query.limit(1).all()
        except Exception as e:
            database_status['status'] = "unhealthy"
            database_status['errors'] = str(e)
            resp = jsonify(database_status)
            resp.status_code = 500

        return resp
