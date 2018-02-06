import logging

from flask import jsonify
from structlog import wrap_logger
from werkzeug.exceptions import InternalServerError
from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.database import db, Status, SecureMessage
from secure_message.repository.saver import Saver
from secure_message.repository.modifier import Modifier


logger = wrap_logger(logging.getLogger(__name__))


class ModifierV2(Modifier):
    """Modifies message to add / remove statuses"""

    @staticmethod
    def add_label(label, message, user, session=db.session):
        """add a label to status table"""
        actor = user.user_uuid

        try:
            status = Status(label=label, msg_id=message['msg_id'], actor=actor)
            session.add(status)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error('Error adding label to repository', msg_id=message, label=label, user_uuid=actor, error=e)
            raise InternalServerError(description="Error adding label to repository")

    @staticmethod
    def remove_label(label, message, user):
        """delete a label from status table"""
        actor = user.user_uuid
        try:
            query = "DELETE FROM securemessage.status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'". \
                format(label, message['msg_id'], actor)
            db.get_engine(app=db.get_app()).execute(query)
            return True
        except Exception as e:
            logger.error('Error removing label from repository', msg_id=message, label=label, user_uuid=actor, error=e)
            raise InternalServerError(description="Error removing label from repository")

