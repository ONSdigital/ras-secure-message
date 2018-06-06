from datetime import datetime
import logging

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from structlog import wrap_logger
from werkzeug.exceptions import InternalServerError

from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.database import db, SecureMessage, Status, Events
from secure_message.services.internal_user_service import InternalUserService


logger = wrap_logger(logging.getLogger(__name__))


class Modifier:
    """Modifies message to add / remove statuses"""

    @staticmethod
    def _get_label_actor(user, message):
        try:
            if user.is_respondent:
                actor = user.user_uuid
            elif message['from_internal']:
                actor = message['msg_from']
            else:
                actor = message['msg_to'][0]
        except KeyError:
            logger.exception("Failed to remove label, no msg_to field")
            raise InternalServerError(description="Error getting actor details from message")

        return actor

    @staticmethod
    def add_label(label, message, user, session=db.session):
        """add a label to status table"""
        actor = Modifier._get_label_actor(user=user, message=message)

        try:
            status = Status(label=label, msg_id=message['msg_id'], actor=actor)
            session.add(status)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error('Error adding label to database', msg_id=message, label=label, user_uuid=actor, error=e)
            raise InternalServerError(description="Error adding label to database")

    @staticmethod
    def remove_label(label, message, user):
        """delete a label from status table"""
        actor = Modifier._get_label_actor(user=user, message=message)

        try:
            query = "DELETE FROM securemessage.status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'". \
                format(label, message['msg_id'], actor)
            db.get_engine(app=db.get_app()).execute(query)
            return True
        except Exception as e:
            logger.error('Error removing label from database', msg_id=message, label=label, user_uuid=actor, error=e)
            raise InternalServerError(description="Error removing label from database")

    @staticmethod
    def add_unread(message, user):
        """Add unread label to status"""
        unread = Labels.UNREAD.value
        inbox = Labels.INBOX.value
        if inbox in message['labels']:
            if unread in message['labels']:
                # Unread label already exists
                return True
            Modifier.add_label(unread, message, user)
            return True
        res = jsonify({'status': 'error'})
        res.status_code = 400
        logging.error('Error adding unread label', status_code=res.status_code)
        return res

    @staticmethod
    def mark_message_as_read(message, user):
        """Remove unread label from status"""
        inbox = Labels.INBOX.value
        unread = Labels.UNREAD.value
        if inbox in message['labels'] and unread in message['labels'] and 'read_date' not in message:
            # Save to both events and secure_message table for now.  In future, the save to the
            # events table will be removed.
            try:
                event = Events(msg_id=message['msg_id'], event=EventsApi.READ.value)
                db.session.add(event)
                secure_message = SecureMessage.query.filter(SecureMessage.msg_id == message['msg_id']).one()
                secure_message.read_at = datetime.utcnow()
                db.session.add(secure_message)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                logger.exception('Error adding read information to message', msg_id=message['msg_id'])
                raise InternalServerError(description="Error adding read information to message")
        Modifier.remove_label(unread, message, user)
        return True

    @staticmethod
    def close_conversation(metadata, user):
        bound_logger = logger.bind(conversation_id=metadata.id, user_id=user.user_uuid)
        bound_logger.info("Getting user details")
        user_details = InternalUserService.get_user_details(user.user_uuid)
        bound_logger.info("Sucessfully retreived user details")

        try:
            bound_logger.info("Closing conversation")
            metadata.is_closed = True
            metadata.closed_at = datetime.utcnow()
            metadata.closed_by = f"{user_details.get('firstName')} {user_details.get('lastName')}"
            metadata.closed_by_uuid = user.user_uuid
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error saving metadata")

        bound_logger.info("Sucessfully closed conversation")
        bound_logger.unbind('conversation_id', 'user_id')

    @staticmethod
    def open_conversation(metadata, user):
        bound_logger = logger.bind(conversation_id=metadata.id, user_id=user.user_uuid)

        try:
            bound_logger.info("Re-opening conversation")
            metadata.is_closed = False
            metadata.closed_at = None
            metadata.closed_by = ''
            metadata.closed_by_uuid = ''
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error saving metadata to conversation")

        bound_logger.info("Sucessfully re-opened conversation")
        bound_logger.unbind('conversation_id', 'user_id')
