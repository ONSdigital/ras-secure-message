import logging
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from structlog import wrap_logger
from werkzeug.exceptions import BadRequest, InternalServerError

from secure_message.common.labels import Labels
from secure_message.repository.database import Conversation, SecureMessage, Status, db
from secure_message.services.service_toggles import internal_user_service

logger = wrap_logger(logging.getLogger(__name__))


class Modifier:
    """Modifies message to add / remove statuses"""

    @staticmethod
    def _get_label_actor(user, message):
        try:
            if user.is_respondent:
                actor = user.user_uuid
            elif message["from_internal"]:
                actor = message["msg_from"]
            else:
                actor = message["msg_to"][0]
        except KeyError:
            logger.exception("Failed to remove label, no msg_to field")
            raise InternalServerError(description="Error getting actor details from message")

        return actor

    @staticmethod
    def add_label(label, message, user, session=db.session):
        """add a label to status table"""
        actor = Modifier._get_label_actor(user=user, message=message)

        try:
            status = Status(label=label, msg_id=message["msg_id"], actor=actor)
            session.add(status)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error("Error adding label to database", msg_id=message, label=label, user_uuid=actor, error=e)
            raise InternalServerError(description="Error adding label to database")

    @staticmethod
    def remove_label(label, message, user):
        """delete a label from status table"""
        actor = Modifier._get_label_actor(user=user, message=message)

        try:
            query = "DELETE FROM securemessage.status WHERE label = '{0}' and msg_id = '{1}' and actor = '{2}'".format(
                label, message["msg_id"], actor
            )
            db.engine.execute(query)
            return True
        except Exception as e:
            logger.error("Error removing label from database", msg_id=message, label=label, user_uuid=actor, error=e)
            raise InternalServerError(description="Error removing label from database")

    @staticmethod
    def add_unread(message: dict, user) -> bool:
        """Add unread label to status

        :raises BadRequest: Raised when message doesn't have an INBOX label
        """
        logger.info("Attempting to add unread label to message", msg_id=message["msg_id"], labels=message["labels"])
        unread = Labels.UNREAD.value
        inbox = Labels.INBOX.value
        if inbox in message["labels"]:
            if unread in message["labels"]:
                # Unread label already exists
                return True
            Modifier.add_label(unread, message, user)
            return True

        logger.error("Error adding unread label. Message is missing INBOX label")
        raise BadRequest(description="Error adding unread label. Message is missing INBOX label")

    @staticmethod
    def mark_message_as_read(message, user):
        """Remove unread label from status"""
        logger.debug("marking message as read with id", message=message["msg_id"])
        # if message is part of a thread mark all messages as read
        if message["thread_id"]:
            Modifier._mark_all_read(message["thread_id"], user)
        else:
            # mark the message as read i.e. remove the unread label and set the `read at` time.
            Modifier._mark_read(message, user)
        # return true as this what the original method did and there seems to be a weird pattern of either returning
        # a response or a boolean for every function throughout this application.
        return True

    @staticmethod
    def _mark_all_read(thread_id, user):
        inbox = Labels.INBOX.value
        unread = Labels.UNREAD.value
        try:
            secure_messages = SecureMessage.query.filter(SecureMessage.thread_id == thread_id)
            for secure_message in secure_messages.all():
                message = secure_message.serialize(user)
                if inbox in message["labels"] and unread in message["labels"]:
                    secure_message.read_at = datetime.utcnow()
                    db.session.add(secure_message)
                    Modifier.remove_label(Labels.UNREAD.value, message, user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error marking thread as read", thread_id=thread_id)
            raise InternalServerError(description="Error marking thread as read")

    @staticmethod
    def _mark_read(message, user):
        inbox = Labels.INBOX.value
        unread = Labels.UNREAD.value
        # message is unread if it has an UNREAD label and the `read_at` time isn't set
        if inbox in message["labels"] and unread in message["labels"] and "read_date" not in message:
            try:
                secure_message = SecureMessage.query.filter(SecureMessage.msg_id == message["msg_id"]).one()
                secure_message.read_at = datetime.utcnow()
                db.session.add(secure_message)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                logger.exception("Error adding read information to message", msg_id=message["msg_id"])
                raise InternalServerError(description="Error adding read information to message")
        Modifier.remove_label(unread, message, user)

    @staticmethod
    def patch_conversation(request_data: dict, conversation: Conversation):
        """
        Goes through each key of the request and updates the conversation object with it if it doesn't match
        what is in the conversation.  Won't update `is_closed`, `closed_by` and `closed_by_uuid` as these are currently
        handled in a different manner in another function.

        :param request_data: Json containing which fields should be patched
        :param conversation: An object containing the currently saved database data
        """
        bound_logger = logger.bind(conversation_id=conversation.id)

        for field in ["category"]:
            # Looks a bit awkward but getattr/setattr lets us loop over all the fields as we can't access fields
            # in the object like a dictionary.

            if request_data.get(field) and request_data.get(field) != getattr(conversation, field):
                setattr(conversation, field, request_data[field])
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            bound_logger.exception("Database error occurred while opening conversation")
            raise InternalServerError(description="Database error occurred while opening conversation")

    @staticmethod
    def patch_message(request_data: dict, message: SecureMessage):
        """
        Goes through each key of the request and updates the message object with the value if it doesn't match
        what is already in the message.

        :param request_data: Json containing which fields should be patched
        :param message: An dict containing the currently saved database data
        """
        bound_logger = logger.bind(message_id=message.msg_id, request_data=request_data)
        bound_logger.info("Attempting to patch message")
        try:
            changeable_values = ["survey_id", "case_id", "business_id", "exercise_id", "read_at"]
            for key in request_data.keys():
                if key in changeable_values:
                    if request_data.get(key) != getattr(message, key):
                        setattr(message, key, request_data[key])

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            bound_logger.exception("Database error occurred while patching message")
            raise InternalServerError(description="Database error occurred while patching message")

    @staticmethod
    def close_conversation(metadata: Conversation, user):
        bound_logger = logger.bind(conversation_id=metadata.id, user_id=user.user_uuid)
        bound_logger.info("Getting user details")

        user_details = internal_user_service.get_user_details(user.user_uuid)
        bound_logger.info("Successfully retrieved user details")

        try:
            bound_logger.info("Closing conversation")
            metadata.is_closed = True
            metadata.closed_at = datetime.utcnow()
            metadata.closed_by = f"{user_details.get('firstName')} {user_details.get('lastName')}"
            metadata.closed_by_uuid = user.user_uuid
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            bound_logger.exception("Database error occurred while closing conversation")
            raise InternalServerError(description="Database error occurred while closing conversation")

        bound_logger.info("Successfully closed conversation")
        bound_logger.unbind("conversation_id", "user_id")

    @staticmethod
    def open_conversation(metadata: Conversation, user):
        bound_logger = logger.bind(conversation_id=metadata.id, user_id=user.user_uuid)

        try:
            bound_logger.info("Re-opening conversation")
            metadata.is_closed = False
            metadata.closed_at = None
            metadata.closed_by = None
            metadata.closed_by_uuid = None
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            bound_logger.exception("Database error occured while opening conversation")
            raise InternalServerError(description="Database error occured while opening conversation")

        bound_logger.info("Successfully re-opened conversation")
        bound_logger.unbind("conversation_id", "user_id")
