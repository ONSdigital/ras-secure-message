import logging
from app.repository.database import db

from werkzeug.exceptions import InternalServerError
from app.validation.labels import Labels
from app.validation.user import User
from datetime import timezone, datetime
logger = logging.getLogger(__name__)


class Modifier:
    """Modifies message to add / remove statuses"""

    @staticmethod
    def add_label(label, message, user_urn):
        """add a label to status table"""
        actor = user_urn if User(user_urn).is_respondent else message['survey']
        try:
            query = "INSERT INTO status (label, msg_id, actor) VALUES ('{0}','{1}','{2}')". \
                format(label, message['msg_id'], actor)
            db.get_engine(app=db.get_app()).execute(query)
            return True
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def remove_label(label, message, user_urn):
        """delete a label from status table"""
        actor = user_urn if User(user_urn).is_respondent else message['survey']
        try:
            query = "DELETE FROM status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'". \
                format(label, message['msg_id'], actor)
            db.get_engine(app=db.get_app()).execute(query)
            return True
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def add_archived(message, user_urn):
        """Add archived label"""
        archive = Labels.ARCHIVE.value
        if archive not in message['labels']:
            Modifier.add_label(archive, message, user_urn)
            return True

    @staticmethod
    def del_archived(message, user_urn):
        """Remove archive label from status"""
        archive = Labels.ARCHIVE.value
        if archive in message['labels']:
            Modifier.remove_label(archive, message, user_urn)
        return True

    @staticmethod
    def add_unread(message, user_urn):
        """Add unread label to status"""
        unread = Labels.UNREAD.value
        inbox = Labels.INBOX.value
        if inbox in message['labels']:
            Modifier.add_label(unread, message, user_urn)
            return True

    @staticmethod
    def del_unread(message, user_urn):
        """Remove unread label from status"""
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

    @staticmethod
    def del_draft(draft_id, del_status=True):
        """Remove draft from status table and secure message table"""
        del_draft_msg = "DELETE FROM secure_message WHERE msg_id='{0}'".format(draft_id)
        del_draft_status = "DELETE FROM status WHERE msg_id='{0}' AND label='{1}'".format(draft_id, Labels.DRAFT.value)

        try:
            db.get_engine(app=db.get_app()).execute(del_draft_msg)
            if del_status is True:
                db.get_engine(app=db.get_app()).execute(del_draft_status)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def replace_current_draft(draft_id, draft):
        """used to replace draft content in message table"""
        Modifier.del_draft(draft_id, del_status=False)
        save_new_draft = "INSERT INTO secure_message (msg_id, subject, body, thread_id, " \
                         "collection_case, reporting_unit, survey) VALUES ('{0}', '{1}', '{2}', '{3}'," \
                         " '{4}', '{5}', '{6}')"\
                         .format(draft_id, draft.subject, draft.body, draft.thread_id, draft.collection_case, draft.reporting_unit,
                                 draft.survey)

        try:
            db.get_engine(app=db.get_app()).execute(save_new_draft)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error replacing message"))

        if draft.urn_to is not None and len(draft.urn_to) != 0:
            Modifier.replace_current_recipient_status(draft_id, draft.urn_to)

    @staticmethod
    def replace_current_recipient_status(draft_id, draft_to):
        """used to replace the draft INBOX_DRAFT label"""
        del_current_status = "DELETE FROM status WHERE msg_id='{0}' AND label='{1}'" \
            .format(draft_id, Labels.DRAFT_INBOX.value)
        save_new_status = "INSERT INTO status (msg_id, actor, label) VALUES ('{0}', '{1}', '{2}')" \
            .format(draft_id, draft_to, Labels.DRAFT_INBOX.value)

        try:
            db.get_engine(app=db.get_app()).execute(del_current_status)
            db.get_engine(app=db.get_app()).execute(save_new_status)
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error replacing DRAFT_INBOX label"))