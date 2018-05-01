import logging

from flask import jsonify
from structlog import wrap_logger
from werkzeug.exceptions import InternalServerError

from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.database import db, Status
from secure_message.repository.saver import Saver

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
    def add_archived(message, user):
        """Add archived label"""
        archive = Labels.ARCHIVE.value
        if archive not in message['labels']:
            Modifier.add_label(archive, message, user)
            return True
        return False

    @staticmethod
    def del_archived(message, user):
        """Remove archive label from status"""
        archive = Labels.ARCHIVE.value
        if archive in message['labels']:
            Modifier.remove_label(archive, message, user)
        return True

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
    def del_unread(message, user):
        """Remove unread label from status"""
        inbox = Labels.INBOX.value
        unread = Labels.UNREAD.value
        if inbox in message['labels'] and unread in message['labels'] and 'read_date' not in message:
            Saver().save_msg_event(message['msg_id'], EventsApi.READ.value)
        Modifier.remove_label(unread, message, user)
        return True
