import logging
from app.repository.database import db

from werkzeug.exceptions import InternalServerError
from app.validation.labels import Labels
from app.validation.user import User
from datetime import timezone, datetime
from app.repository.saver import Saver
logger = logging.getLogger(__name__)


class Modifier:
    """Modifies message to add / remove statuses"""

    @staticmethod
    def add_label(label, message, user_urn):
        actor = user_urn if User(user_urn).is_respondent else message['survey']
        try:
            query = "INSERT INTO status (label, msg_id, actor) VALUES ('{0}','{1}','{2}')". \
                format(label, message['msg_id'], actor)
            db.get_engine(app=db.get_app()).execute(query)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def remove_label(label, message, user_urn):
        actor = user_urn if User(user_urn).is_respondent else message['survey']
        try:
            query = "DELETE FROM status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'". \
                format(label, message['msg_id'], actor)
            db.get_engine(app=db.get_app()).execute(query)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def add_archived(message, user_urn):
        archive = Labels.ARCHIVE.value
        if archive not in message['labels']:
            Modifier.add_label(archive, message, user_urn)
            return True

    @staticmethod
    def del_archived(message, user_urn, ):
        archive = Labels.ARCHIVE.value
        if archive in message['labels']:
            Modifier.remove_label(archive, message, user_urn)
            return True

    @staticmethod
    def add_unread(message, user_urn):
        unread = Labels.UNREAD.value
        inbox = Labels.INBOX.value
        if inbox in message['labels']:
            Modifier.add_label(unread, message, user_urn)
            return True

    @staticmethod
    def del_unread(message, user_urn):
        inbox = Labels.INBOX.value
        unread = Labels.UNREAD.value
        if inbox in message['labels'] and unread in message['labels'] and message['read_date'] is None:

            query = "UPDATE secure_message SET read_date = '{0}' WHERE msg_id = '{1}'".format(datetime.now(
                    timezone.utc), message['msg_id'])
            try:
                db.get_engine(app=db.get_app()).execute(query)
            except Exception as e:
                logger.error(e)
                raise (InternalServerError(description="Error retrieving messages from database"))
            Modifier.remove_label(unread, message, user_urn)
        return True

    def del_draft(self, message):
        self.remove_label(Labels.DRAFT.value, message, message.urn_from)

    @staticmethod
    def add_sent(message):
        query = "UPDATE secure_message SET sent_date = '{0}' WHERE msg_id = '{1}'".format(datetime.now(timezone.utc),
                                                                                          message.msg_id)
        update_label = "UPDATE status SET label = '{0}' WHERE msg_id = '{1}'".format(Labels.SENT.value, message.msg_id)

        try:
            db.get_engine(app=db.get_app()).execute(query)
            db.get_engine(app=db.get_app()).execute(update_label)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error updating sent_date and sent label"))

    @staticmethod
    def add_inbox_and_unread_for_draft_remove_inbox_draft(message):
        if User(message.urn_to).is_respondent:
            Saver().save_msg_status(message.urn_to, message.msg_id, Labels.INBOX.value)
            Saver().save_msg_status(message.urn_to, message.msg_id, Labels.UNREAD.value)
        else:
            Saver().save_msg_status(message.survey, message.msg_id, Labels.INBOX.value)
            Saver().save_msg_status(message.survey, message.msg_id, Labels.UNREAD.value)
