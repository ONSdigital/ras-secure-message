import logging
from structlog import wrap_logger
from app.exception.exceptions import MessageSaveException
from app.repository.database import db, SecureMessage, Status, Events, InternalSentAudit

logger = wrap_logger(logging.getLogger(__name__))


class Saver:
    """Created when saving a message"""

    @staticmethod
    def save_message(domain_message, session=db.session):
        """save message to database"""

        db_message = SecureMessage()
        db_message.set_from_domain_model(domain_message)
        try:
            session.add(db_message)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error('Message save failed', error=e)
            raise MessageSaveException(e)

    @staticmethod
    def save_msg_status(actor, msg_id, label, session=db.session):
        """save message status to database"""

        db_status_to = Status()
        db_status_to.set_from_domain_model(msg_id, actor, label)
        try:
            session.add(db_status_to)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error('Message status save failed', error=e)
            raise MessageSaveException(e)

    @staticmethod
    def save_msg_event(msg_id, event, session=db.session):
        """save message events to events database"""

        event = Events(msg_id=msg_id, event=event)

        try:
            session.add(event)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error('Message event save failed', error=e)
            raise MessageSaveException(e)

    @staticmethod
    def save_msg_audit(msg_id, msg_urn, session=db.session):
        """Save Sent Audit data to database"""
        db_audit = InternalSentAudit()
        db_audit.set_from_domain_model(msg_id, msg_urn)
        try:
            session.add(db_audit)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error('Message audit save failed', error=e)
            raise MessageSaveException(e)
