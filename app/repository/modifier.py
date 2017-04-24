import logging
from app.repository.database import db

from werkzeug.exceptions import InternalServerError
from app.repository.saver import Saver
from app.validation.labels import Labels
from app.validation.user import User
from datetime import timezone, datetime

logger = logging.getLogger(__name__)


class Modifier:
    """Modifies message to add / remove statuses"""

    @staticmethod
    def remove_label(user_urn, message_id, survey, label):
        if User(user_urn).is_respondent:
            query = "DELETE FROM status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'".\
                format(label, message_id, user_urn)
        else:
            query = "DELETE FROM status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'".\
                format(label, message_id, survey)

        try:
            db.get_engine(app=db.get_app()).execute(query)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def add_archived(message, user_urn):
        if Labels.ARCHIVE.value not in message['labels']:
            if User(user_urn).is_respondent:
                Saver().save_msg_status(message['urn_from'], message['msg_id'], Labels.ARCHIVE.value)
            else:
                Saver().save_msg_status(message['survey'], message['msg_id'], Labels.ARCHIVE.value)
            return True

    def del_archived(self, message, user_urn):
        if Labels.ARCHIVE.value in message['labels']:
            self.remove_label(user_urn, message['msg_id'], message['survey'], Labels.ARCHIVE.value)
            return True

    @staticmethod
    def add_unread(message, user_urn):
        if Labels.INBOX.value in message['labels']:
            if User(user_urn).is_respondent:
                Saver().save_msg_status(message['urn_form'], message['msg_id'], Labels.UNREAD.value)
            else:
                Saver().save_msg_status(message['survey'], message['msg_id'], Labels.UNREAD.value)
            return True

    def del_unread(self, message, user_urn):

        if Labels.INBOX.value in message['labels'] and Labels.UNREAD.value in message['labels']:
            if message['read_date'] is None:
                query = "UPDATE secure_message SET read_date = '{0}' WHERE msg_id = '{1}'".format(datetime.now(
                    timezone.utc), message['msg_id'])

                try:
                    db.get_engine(app=db.get_app()).execute(query)
                except Exception as e:
                    logger.error(e)
                    raise (InternalServerError(description="Error retrieving messages from database"))

            self.remove_label(user_urn, message['msg_id'], message['survey'], Labels.UNREAD.value)
            return True
