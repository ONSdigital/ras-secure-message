import logging
from structlog import wrap_logger
from werkzeug.exceptions import InternalServerError

from app.common.labels import Labels
from app.repository.database import db, Status, SecureMessage, Events
from app.repository.saver import Saver

logger = wrap_logger(logging.getLogger(__name__))


class Modifier:
    """Modifies message to add / remove statuses"""

    @staticmethod
    def add_label(label, message, user, session=db.session):
        """add a label to status table"""
        actor = user.user_uuid if user.is_respondent else message['survey']

        try:
            status = Status(label=label, msg_id=message['msg_id'], actor=actor)
            session.add(status)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def remove_label(label, message, user):
        """delete a label from status table"""
        actor = user.user_uuid if user.is_respondent else message['survey']
        try:
            query = "DELETE FROM status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'". \
                format(label, message['msg_id'], actor)
            db.get_engine(app=db.get_app()).execute(query)
            return True
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def add_archived(message, user):
        """Add archived label"""
        archive = Labels.ARCHIVE.value
        if archive not in message['labels']:
            Modifier.add_label(archive, message, user)
            return True

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
            Modifier.add_label(unread, message, user)
            return True

    @staticmethod
    def del_unread(message, user):
        """Remove unread label from status"""
        inbox = Labels.INBOX.value
        unread = Labels.UNREAD.value
        if inbox in message['labels'] and unread in message['labels'] and 'read_date' not in message:
            Saver().save_msg_event(message['msg_id'], 'Read')
        Modifier.remove_label(unread, message, user)
        return True

    @staticmethod
    def del_draft(draft_id, del_status=True, del_event=True):
        """Remove draft from status table and secure message table"""
        del_draft_msg = "DELETE FROM secure_message WHERE msg_id='{0}'".format(draft_id)
        del_draft_status = "DELETE FROM status WHERE msg_id='{0}' AND label='{1}'".format(draft_id, Labels.DRAFT.value)
        del_draft_event = "DELETE FROM events WHERE msg_id='{0}'".format(draft_id)
        del_draft_inbox_status = "DELETE FROM status WHERE msg_id='{0}' AND label='{1}'".format(draft_id, Labels.DRAFT_INBOX.value)

        try:
            db.get_engine(app=db.get_app()).execute(del_draft_msg)
            if del_status is True:
                db.get_engine(app=db.get_app()).execute(del_draft_status)
                db.get_engine(app=db.get_app()).execute(del_draft_inbox_status)

            if del_event is True:
                db.get_engine(app=db.get_app()).execute(del_draft_event)

        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving messages from database"))

    @staticmethod
    def replace_current_draft(draft_id, draft, session=db.session):
        """used to replace draft content in message table"""
        Modifier.del_draft(draft_id, del_status=False)
        secure_message = SecureMessage(msg_id=draft_id, subject=draft.subject, body=draft.body,
                                       thread_id=draft.thread_id, collection_case=draft.collection_case,
                                       ru_id=draft.ru_id, collection_exercise=draft.collection_exercise,
                                       survey=draft.survey)

        try:
            session.add(secure_message)
            session.commit()
        except Exception as e:
            session.rollbeck()
            logger.error(e)
            raise (InternalServerError(description="Error replacing message"))

        Saver().save_msg_event(draft_id, 'Draft_Saved')

        if draft.msg_to is not None and len(draft.msg_to) != 0:
            Modifier.replace_current_recipient_status(draft_id, draft.msg_to)

    @staticmethod
    def replace_current_recipient_status(draft_id, draft_to, session=db.session):
        """used to replace the draft INBOX_DRAFT label"""
        del_current_status = "DELETE FROM status WHERE msg_id='{0}' AND label='{1}'" \
            .format(draft_id, Labels.DRAFT_INBOX.value)
        # TODO: Only handling first item in list.
        new_status = Status(msg_id=draft_id, actor=draft_to[0], label=Labels.DRAFT_INBOX.value)

        try:
            db.get_engine(app=db.get_app()).execute(del_current_status)
            session.add(new_status)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(e)
            raise (InternalServerError(description="Error replacing DRAFT_INBOX label"))
