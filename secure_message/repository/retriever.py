import logging

from flask import jsonify
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from structlog import wrap_logger
from werkzeug.exceptions import Forbidden, InternalServerError, NotFound

from secure_message.common.labels import Labels
from secure_message.common.utilities import set_conversation_type_args
from secure_message.constants import NON_SPECIFIC_INTERNAL_USER
from secure_message.repository.database import Conversation, SecureMessage, Status, db

logger = wrap_logger(logging.getLogger(__name__))


class Retriever:
    """Created when retrieving messages"""

    @staticmethod
    def unread_message_count(user):
        """Count users unread messages"""
        logger.info("Getting unread message count", user_uuid=user.user_uuid)
        status_conditions = [Status.actor == str(user.user_uuid)]
        try:
            result = (
                SecureMessage.query.join(Status)
                .filter(and_(*status_conditions))
                .filter(Status.label == "UNREAD")
                .count()
            )
        except Exception:
            logger.exception("Error retrieving count of unread messages from database")
            raise InternalServerError(description="Error retrieving count of unread messages from database")
        return result

    @staticmethod
    def thread_count_by_survey(request_args, user):
        """Count users threads for a specific survey"""

        conditions = []
        conversation_condition = [Conversation.is_closed.is_(request_args.is_closed)]

        if request_args.surveys:
            conditions.append(SecureMessage.survey_id.in_(request_args.surveys))

        if request_args.business_id:
            conditions.append(SecureMessage.business_id == request_args.business_id)

        if request_args.cc:
            conditions.append(SecureMessage.case_id == request_args.cc)

        if request_args.ce:
            conditions.append(SecureMessage.exercise_id == request_args.ce)

        if request_args.category:
            conversation_condition.append(Conversation.category == request_args.category)

        if request_args.my_conversations:
            conditions.append(Status.actor == user.user_uuid)
            conditions.append(Status.msg_id == SecureMessage.msg_id)

        if request_args.new_respondent_conversations:
            conditions.append(Status.msg_id == SecureMessage.msg_id)
            conditions.append(Status.actor == NON_SPECIFIC_INTERNAL_USER)

        try:
            result = (
                SecureMessage.query.join(Conversation).join(Status).filter(*conversation_condition)
                .filter(and_(*conditions)).distinct(SecureMessage.msg_id).count()
            )
        except Exception as e:
            logger.error("Error retrieving count of threads by survey from database", error=e)
            raise InternalServerError(description="Error retrieving count of threads from database")
        return result

    @staticmethod
    def thread_count_by_survey_and_conversation_states(request_args, user):
        """Return 4 conversation counts. They are for open, closed, my conversations and
        new_respondent_conversation.
        Given each of these counts uses different clauses to define them and they are not mutually exclusive,
        they are difficult to achieve with the current db structure in a single query, hence this submits 4 db queries.
        """

        totals = {}

        args = set_conversation_type_args(request_args)  # is_closed defaults to False
        totals["open"] = Retriever.thread_count_by_survey(args, user)

        args = set_conversation_type_args(request_args, is_closed=True)
        totals["closed"] = Retriever.thread_count_by_survey(args, user)

        args = set_conversation_type_args(request_args, my_conversations=True)
        totals["my_conversations"] = Retriever.thread_count_by_survey(args, user)

        args = set_conversation_type_args(request_args, new_conversations=True)
        totals["new_respondent_conversations"] = Retriever.thread_count_by_survey(args, user)

        return totals

    @staticmethod
    def retrieve_thread_list(user, request_args):
        """returns list of threads from db"""
        if user.is_respondent:
            return Retriever._retrieve_respondent_thread_list(request_args, user)

        return Retriever._retrieve_internal_thread_list(request_args, user)

    @staticmethod
    def _retrieve_respondent_thread_list(request_args, user):
        conditions = []

        if request_args.business_id:
            conditions.append(SecureMessage.business_id == request_args.business_id)

        if request_args.surveys:
            conditions.append(SecureMessage.survey_id.in_(request_args.surveys))

        if request_args.cc:
            conditions.append(SecureMessage.case_id == request_args.cc)

        if request_args.ce:
            conditions.append(SecureMessage.exercise_id == request_args.ce)

        try:
            t = (
                db.session.query(SecureMessage.thread_id, func.max(SecureMessage.id).label("max_id"))
                .join(Conversation)
                .join(Status)
                .filter(Status.actor == user.user_uuid)
                .filter(Conversation.is_closed.is_(request_args.is_closed))
                .group_by(SecureMessage.thread_id)
                .subquery("t")
            )

            conditions.append(SecureMessage.thread_id == t.c.thread_id)
            conditions.append(SecureMessage.id == t.c.max_id)

            result = (
                SecureMessage.query.filter(and_(*conditions))
                .order_by(t.c.max_id.desc())
                .paginate(request_args.page, request_args.limit, False)
            )

        except SQLAlchemyError:
            logger.exception("Error retrieving messages from database")
            raise InternalServerError(description="Error retrieving messages from database")

        return result

    @staticmethod
    def _retrieve_internal_thread_list(request_args, user):
        """Retrieve a list of threads for an internal user"""
        conditions = []
        logger.info("Retrieving list of threads for internal user", user_uuid=user.user_uuid)

        if request_args.business_id:
            conditions.append(SecureMessage.business_id == request_args.business_id)

        if request_args.surveys:
            conditions.append(SecureMessage.survey_id.in_(request_args.surveys))

        if request_args.cc:
            conditions.append(SecureMessage.case_id == request_args.cc)

        if request_args.ce:
            conditions.append(SecureMessage.exercise_id == request_args.ce)

        try:
            subquery_filter = [Conversation.is_closed.is_(request_args.is_closed)]

            if request_args.category:
                subquery_filter.append(Conversation.category == request_args.category)

            t = (
                db.session.query(SecureMessage.thread_id, func.max(SecureMessage.id).label("max_id"))
                .join(Conversation)
                .filter(and_(*subquery_filter))
                .group_by(SecureMessage.thread_id)
                .subquery("t")
            )

            conditions.append(SecureMessage.thread_id == t.c.thread_id)
            conditions.append(SecureMessage.id == t.c.max_id)

            # If my_conversations make sure that the user is an actor in the last message in the thread
            if request_args.my_conversations:
                conditions.append(Status.actor == user.user_uuid)
                conditions.append(Status.msg_id == SecureMessage.msg_id)

            # If new_respondent_conversations the actor should be NON_SPECIFIC_INTERNAL_USER i.e Group
            if request_args.new_respondent_conversations:
                conditions.append(Status.actor == NON_SPECIFIC_INTERNAL_USER)
                conditions.append(Status.label == Labels.INBOX.value)
                conditions.append(Status.msg_id == SecureMessage.msg_id)

            result = (
                SecureMessage.query.filter(and_(*conditions))
                .order_by(t.c.max_id.desc())
                .paginate(request_args.page, request_args.limit, False)
            )

        except SQLAlchemyError:
            logger.exception("Error retrieving messages from database")
            raise InternalServerError(description="Error retrieving messages from database")

        return result

    @staticmethod
    def retrieve_populated_message_object(message_id: str) -> SecureMessage:
        """
        Gets a single message from the secure_message table

        :param message_id: The 'msg_id' of the message
        :return: A SecureMessage object containing the data from the database about the message
        """
        logger.info("Retrieving message", message_id=message_id)
        try:
            result = SecureMessage.query.filter_by(msg_id=message_id).one()
            if result is None:
                logger.info("Message ID not found", message_id=message_id)
                raise NotFound(description=f"Message with msg_id '{message_id}' does not exist")
        except SQLAlchemyError:
            logger.exception("Error retrieving message from database")
            raise InternalServerError(description="Error retrieving message from database")

        return result

    @staticmethod
    def retrieve_message(message_id: str, user) -> dict:
        """returns single message from db.  Comes with additional metadata around labels"""
        db_model = SecureMessage()
        logger.info("Retrieving message", message_id=message_id)
        try:
            result = db_model.query.filter_by(msg_id=message_id).first()
            if result is None:
                logger.info("Message ID not found", message_id=message_id)
                raise NotFound(description=f"Message with msg_id '{message_id}' does not exist")
        except SQLAlchemyError:
            logger.exception("Error retrieving message from database")
            raise InternalServerError(description="Error retrieving message from database")

        return result.serialize(user)

    @staticmethod
    def retrieve_thread(thread_id, user):
        if user.is_respondent:
            logger.info("Retrieving messages in thread for respondent", thread_id=thread_id, user_uuid=user.user_uuid)
            return Retriever._retrieve_thread_for_respondent(thread_id, user)
        logger.info("Retrieving messages in thread for internal user", thread_id=thread_id, user_uuid=user.user_uuid)
        return Retriever._retrieve_thread_for_internal_user(thread_id)

    @staticmethod
    def _retrieve_thread_for_respondent(thread_id, user):
        """returns list of messages for thread id for a respondent"""
        try:
            result = SecureMessage.query.join(Conversation).join(Status).filter(SecureMessage.thread_id == thread_id)

            if not result.all():
                logger.info("Thread does not exist", thread_id=thread_id, user_id=user.user_uuid)
                raise NotFound(description=f"Conversation with thread_id '{thread_id}' does not exist")

            result = result.filter(Status.actor == user.user_uuid).order_by(SecureMessage.id.desc())

            if not result.all():
                logger.info(
                    "Thread found, but respondent does not have access", thread_id=thread_id, user_id=user.user_uuid
                )
                raise Forbidden(
                    description=f"User {user.user_uuid} is not authorised to view conversation with thread_id: "
                    f"'{thread_id}'"
                )

        except SQLAlchemyError:
            logger.exception("Error retrieving conversation from database")
            raise InternalServerError(description="Error retrieving conversation from database")

        return result

    @staticmethod
    def _retrieve_thread_for_internal_user(thread_id: str):
        """returns paginated list of messages for thread id for an internal user"""

        try:
            result = (
                SecureMessage.query.join(Status)
                .filter(SecureMessage.thread_id == thread_id)
                .filter(
                    or_(
                        and_(SecureMessage.from_internal.is_(False), Status.label == Labels.INBOX.value),  # NOQA
                        and_(SecureMessage.from_internal.is_(True), Status.label.in_([Labels.SENT.value])),
                    )
                )
                .order_by(Status.id.desc())
            )

            if not result.all():
                logger.info("Thread not retrieved for internal user", thread_id=thread_id)
                raise NotFound(description=f"Conversation with thread_id {thread_id} not retrieved")

        except SQLAlchemyError:
            logger.exception("Error retrieving conversation from database", thread_id=thread_id)
            raise InternalServerError(description=f"Error retrieving conversation '{thread_id}' from database")

        return result

    @staticmethod
    def retrieve_conversation_metadata(thread_id):
        result = Conversation.query.filter(Conversation.id == thread_id)
        try:
            return result.one()
        except NoResultFound:
            logger.info("No conversation found", thread_id=thread_id)
            return None

    @staticmethod
    def check_db_connection():
        """checks if db connection is working"""
        try:
            SecureMessage().query.limit(1).all()
        except Exception as e:
            logger.exception("No connection to database")
            response = jsonify({"status": "unhealthy", "errors": str(e)})
            response.status_code = 500
            return response

        return jsonify({"status": "healthy", "errors": "none"})
