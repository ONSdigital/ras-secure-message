import logging

from app.exception.exceptions import MessageSaveException
from app.repository import database
from app.repository.database import db
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Saver:
    """Created when saving a message"""

    @staticmethod
    def save_message(domain_message):
        """save message to database"""

        db_message = database.SecureMessage()
        domain_message.sent_date = datetime.now(timezone.utc)  # LOGIC NEEDED: set sent_date only for sent message
        db_message.set_from_domain_model(domain_message)
        try:
            db.session.add(db_message)
            db.session.commit()
        except Exception as e:
            logger.error("Message save failed {}".format(e))
            raise MessageSaveException(e)

    @staticmethod
    def convert_to_datamodel(domain_message):
        return database.SecureMessage(domain_message.msg_to, domain_message.msg_from, domain_message.subject,
                                      domain_message.body, domain_message.thread_id, domain_message.sent_date,
                                      domain_message.read_date, domain_message.msg_id)

    @staticmethod
    def save_msg_status(msg_id, msg_urn, label):
        """save message status to database"""

        db_status_to = database.Status()
        db_status_to.set_from_domain_model(msg_id, msg_urn, label)
        try:
            db.session.add(db_status_to)
            db.session.commit()
        except Exception as e:
            logger.error("Message status save failed {}".format(e))
            raise MessageSaveException(e)

    @staticmethod
    def save_msg_audit(msg_id, msg_urn):

        db_audit = database.InternalSentAudit()
        db_audit.set_from_domain_model(msg_id, msg_urn)
        try:
            db.session.add(db_audit)
            db.session.commit()
        except Exception as e:
            logger.error("Message audit save failed {}".format(e))
            raise MessageSaveException(e)



