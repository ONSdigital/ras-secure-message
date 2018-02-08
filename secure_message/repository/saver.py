import logging

from sqlalchemy.exc import SQLAlchemyError
from structlog import wrap_logger
from secure_message.exception.exceptions import MessageSaveException
from secure_message.repository.database import Actors, db, SecureMessage, Status, Events, InternalSentAudit

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
        except SQLAlchemyError:
            session.rollback()
            logger.exception('Secure message save failed')
            raise MessageSaveException('Message save failed')

    @staticmethod
    def save_msg_status(actor, msg_id, label, session=db.session):
        """save message status to database"""
        db_status_to = Status()
        db_status_to.set_from_domain_model(msg_id, actor, label)

        try:
            session.add(db_status_to)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.exception('Message status save failed')
            raise MessageSaveException('Message save failed')

    @staticmethod
    def save_msg_event(msg_id, event, session=db.session):
        """save message events to events database"""
        event = Events(msg_id=msg_id, event=event)

        try:
            session.add(event)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.exception('Message event save failed')
            raise MessageSaveException('Message save failed')

    @staticmethod
    def save_msg_audit(msg_id, msg_urn, session=db.session):
        """Save Sent Audit data to database"""
        db_audit = InternalSentAudit()
        db_audit.set_from_domain_model(msg_id, msg_urn)

        try:
            session.add(db_audit)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.exception('Message audit save failed')
            raise MessageSaveException('Message save failed')

    @staticmethod
    def save_msg_actors(msg_id, from_actor, to_actor, sent_from_internal, session=db.session):
        """Save actor information data to database"""
        actor = Actors(msg_id, from_actor, to_actor, sent_from_internal)

        try:
            session.add(actor)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.exception('Message actor save failed')
            raise MessageSaveException('Message save failed')
