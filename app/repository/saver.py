import logging

from app.exception.exceptions import MessageSaveException
from app.repository import database
from app.repository.database import db

logger = logging.getLogger(__name__)


class Saver:
    """Created when saving a message"""

    @staticmethod
    def save_message(domain_message):
        """save message to database"""
        db_message = database.DbMessage()
        db_message.set_from_domain_model(domain_message)
        try:
            db.session.add(db_message)
            db.session.commit()
        except Exception as e:
            logger.error("Message save failed {}".format(e))
            raise MessageSaveException(e)

    @staticmethod
    def convert_to_datamodel(domain_message):
        return database.DbMessage(domain_message.msg_to, domain_message.msg_from, domain_message.subject,
                                  domain_message.body, domain_message.thread_id, domain_message.sent_date,
                                  domain_message.read_date, domain_message.msg_id)
