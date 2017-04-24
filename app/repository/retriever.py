import logging

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, NotFound

from app.repository.database import SecureMessage

logger = logging.getLogger(__name__)


class Retriever:
    """Created when retrieving messages"""
    @staticmethod
    def retrieve_message_list(page, limit):
        """returns list of messages from db"""
        db_model = SecureMessage()

        try:
            result = db_model.query.order_by('sent_date desc').paginate(page, limit, False)
        except Exception as e:
            logger.error(e)
            raise(InternalServerError(description="Error retrieving messages from database"))

        return True, result

    @staticmethod
    def retrieve_message(message_id, user_urn):
        """returns single message from db"""
        db_model = SecureMessage()

        try:
            result = db_model.query.filter_by(msg_id=message_id).first()
            if result is None:
                raise (NotFound(description="Message with msg_id '{0}' does not exist".format(message_id)))
        except SQLAlchemyError as e:
            logger.error(e)
            raise(InternalServerError(description="Error retrieving message from database"))

        message = result.serialize(user_urn)

        return message

    @staticmethod
    def check_db_connection():
        """checks if db connection is working"""
        database_status = {"status": "healthy", "errors": "none"}
        resp = jsonify(database_status)
        resp.status_code = 200

        try:
            SecureMessage().query.limit(1).all()
        except Exception as e:
            database_status['status'] = "unhealthy"
            database_status['errors'] = str(e)
            resp = jsonify(database_status)
            resp.status_code = 500

        return resp
