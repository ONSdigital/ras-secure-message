import logging

from sqlalchemy.exc import SQLAlchemyError
from structlog import wrap_logger
from secure_message.exception.exceptions import MessageSaveException
from secure_message.repository.database import db, Conversation, Events, SecureMessage, Status

logger = wrap_logger(logging.getLogger(__name__))


class Saver:
    """Created when saving a message"""

    @staticmethod
    def save_message(domain_message, session=db.session):
        """save message to database"""
        db_message = SecureMessage()
        db_message.set_from_domain_model(domain_message)

        try:
            # We only want to do this if it's the first message in a conversation.
            if db_message.msg_id == db_message.thread_id:
                logger.info("Setting thread id", thread_id=db_message.thread_id)
                conversation = Conversation()
                conversation.id = db_message.thread_id
                if hasattr(domain_message, 'category'):
                    logger.info("setting message category as", category=domain_message.category)
                    conversation.category = domain_message.category
                else:
                    logger.info("category not defined, hence defaulting to Survey")

                session.add(conversation)
                session.flush()

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
