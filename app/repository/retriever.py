from app.data_model.database import DbMessage
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class Retriever:
    """Created when retrieving messages"""
    @staticmethod
    def retrieve_message_list(page, limit):
        """returns list of messages from db"""
        db_model = DbMessage()

        try:
            result = db_model.query.order_by('sent_date desc').paginate(page, limit, False)
        except Exception as e:
            logger.error(e)
            return False

        return True, result

    @staticmethod
    def retrieve_message(message_id):
        """returns single message from db"""
        db_model = DbMessage()
        result = db_model.query.filter_by(id=message_id).first_or_404()
        return jsonify(result.serialize)

    @staticmethod
    def check_db_connection():
        """checks if db connection is working"""
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
