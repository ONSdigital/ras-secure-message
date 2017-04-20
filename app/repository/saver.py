import logging

from app.exception.exceptions import MessageSaveException
from app.repository import database
from app.repository.database import db
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Saver:
    """Created when saving a message"""

    @staticmethod
    def save_message(domain_message, session=db.session):
        """save message to database"""

        db_message = database.SecureMessage()
        domain_message.sent_date = datetime.now(timezone.utc)  # LOGIC NEEDED: set sent_date only for sent message
        db_message.set_from_domain_model(domain_message)
        try:
            session.add(db_message)
            session.commit()
        except Exception as e:
            logger.error("Message save failed {0}".format(e))
            raise MessageSaveException(e)

    @staticmethod
    def save_msg_status(msg_urn, msg_id, label, session=db.session):
        """save message status to database"""

        db_status_to = database.Status()
        db_status_to.set_from_domain_model(msg_id, msg_urn, label)
        try:
            session.add(db_status_to)
            session.commit()
        except Exception as e:
            logger.error("Message status save failed {}".format(e))
            raise MessageSaveException(e)

    @staticmethod
    def save_msg_audit(msg_id, msg_urn, session=db.session):
        """Save Sent Audit data to database"""
        db_audit = database.InternalSentAudit()
        db_audit.set_from_domain_model(msg_id, msg_urn)
        try:
            session.add(db_audit)
            session.commit()
        except Exception as e:
            logger.error("Message audit save failed {}".format(e))
            raise MessageSaveException(e)
