import logging
from app.repository.database import db

from werkzeug.exceptions import InternalServerError

from app.exception.exceptions import MessageSaveException
from app.repository import database
from app.repository.database import db, Status
from app.repository.retriever import Retriever
from datetime import datetime, timezone
from app.repository.saver import Saver
from app.validation.labels import Labels

logger = logging.getLogger(__name__)


class Modifier:
    """Modifies message to add / remove statuses"""

    @staticmethod
    def remove_label(user_urn, message_id, survey, label):
        if "respondent" in user_urn:
            query = "DELETE FROM status WHERE label = '{}' and msg_id = '{}' and actor = '{}'".format(label, message_id,
                                                                                                user_urn)
        else:
            query = "DELETE FROM status WHERE label = '{}' and msg_id = '{}' and actor = '{}'".format(label, message_id,survey)

        try:
            result = db.get_engine(app=db.get_app()).execute(query)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))



    @staticmethod
    def add_archived(message, message_id, user_urn):
        if Labels.ARCHIVE.value not in message['labels']:
            if "respondent" in user_urn:
                Saver().save_msg_status(message['urn_from'], message['msg_id'], Labels.ARCHIVE.value)
            else:
                Saver().save_msg_status(message['survey'], message['msg_id'], Labels.ARCHIVE.value)
            return True


    def del_archived(self,message, message_id, user_urn):
        # Retriever.retrieve_message(message_id, user_urn)
        if Labels.ARCHIVE.value in message['labels']:
            self.remove_label(user_urn, message_id, message['survey'], Labels.ARCHIVE.value)
            return True

    @staticmethod
    def add_unread(message, message_id, user_urn):

        if Labels.INBOX.value in message['labels']:
            if "respondent" in user_urn:
                Saver().save_msg_status(message['urn_form'], message['msg_id'], Labels.UNREAD.value)
            else:
                Saver().save_msg_status(message['survey'], message['msg_id'], Labels.UNREAD.value)
            return True

    def del_unread(self,message, message_id, user_urn):

        if Labels.INBOX.value in message ['labels'] and Labels.UNREAD.value in message['labels']:
            self.remove_label(user_urn, message_id, message['survey'], Labels.UNREAD.value)
            return True