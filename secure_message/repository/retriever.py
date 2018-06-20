import logging

from flask import abort, g, jsonify
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from structlog import wrap_logger
from werkzeug.exceptions import InternalServerError, NotFound

from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.database import Conversation, db, Events, SecureMessage, Status

logger = wrap_logger(logging.getLogger(__name__))


class Retriever:
    """Created when retrieving messages"""

    @staticmethod
    def unread_message_count(user):
        """Count users unread messages"""
        logger.info("Getting unread message count", user_uuid=user.user_uuid)
        status_conditions = [Status.actor == str(user.user_uuid)]
        try:
            result = SecureMessage.query.join(Status).filter(and_(*status_conditions)).filter(
                Status.label == 'UNREAD').count()
        except Exception:
            logger.exception('Error retrieving count of unread messages from database')
            raise InternalServerError(description="Error retrieving count of unread messages from database")
        return result

    @staticmethod
    def thread_count_by_survey(user, survey, is_closed):
        """Count users threads for a specific survey"""

        if not user.is_internal:
            logger.info("Thread count should be internal users only", user_uuid=g.user.user_uuid)
            abort(403)

        survey_conditions = []

        if survey:
            survey_conditions.append(SecureMessage.survey.in_(survey))
        else:
            survey_conditions.append(True)

        try:
            result = SecureMessage.query.join(Conversation) \
                .filter(Conversation.is_closed.is_(is_closed)) \
                .filter(*survey_conditions) \
                .distinct(SecureMessage.thread_id) \
                .count()
        except Exception as e:
            logger.error('Error retrieving count of threads by survey from database', error=e)
            raise InternalServerError(description="Error retrieving count of threads from database")
        return result

    @staticmethod
    def retrieve_thread_list(user, request_args):
        """returns list of threads from db"""
        if user.is_respondent:
            return Retriever._retrieve_respondent_thread_list(request_args, user)

        return Retriever._retrieve_internal_thread_list(request_args, user)

    @staticmethod
    def _retrieve_respondent_thread_list(request_args, user):
        conditions = []
        actor_conditions = []

        if user.is_respondent:
            logger.info("Retrieving list of threads for respondent", user_uuid=user.user_uuid)
            actor_conditions.append(Status.actor == str(user.user_uuid))

        if request_args.ru_id:
            conditions.append(SecureMessage.ru_id == request_args.ru_id)

        if request_args.surveys:
            conditions.append(SecureMessage.survey.in_(request_args.surveys))

        if request_args.cc:
            conditions.append(SecureMessage.collection_case == request_args.cc)

        if request_args.ce:
            conditions.append(SecureMessage.collection_exercise == request_args.ce)

        try:
            t = db.session.query(SecureMessage.thread_id, func.max(SecureMessage.id)  # pylint:disable=no-member
                                 .label('max_id')) \
                .join(Conversation) \
                .filter(Conversation.is_closed.is_(request_args.is_closed)) \
                .group_by(SecureMessage.thread_id).subquery('t')

            conditions.append(SecureMessage.thread_id == t.c.thread_id)
            conditions.append(SecureMessage.id == t.c.max_id)

            result = SecureMessage.query.filter(and_(*conditions)) \
                .order_by(t.c.max_id.desc()).paginate(request_args.page, request_args.limit, False)

        except SQLAlchemyError:
            logger.exception('Error retrieving messages from database')
            raise InternalServerError(description="Error retrieving messages from database")

        return result

    @staticmethod
    def _retrieve_internal_thread_list(request_args, user):
        """Retrieve a list of threads for an internal user"""
        conditions = []

        logger.info("Retrieving list of threads for internal user", user_uuid=user.user_uuid)

        if request_args.ru_id:
            conditions.append(SecureMessage.ru_id == request_args.ru_id)

        if request_args.surveys:
            conditions.append(SecureMessage.survey.in_(request_args.surveys))

        if request_args.cc:
            conditions.append(SecureMessage.collection_case == request_args.cc)

        if request_args.ce:
            conditions.append(SecureMessage.collection_exercise == request_args.ce)

        try:
            t = db.session.query(SecureMessage.thread_id, func.max(SecureMessage.id)  # pylint:disable=no-member
                                 .label('max_id')) \
                .join(Conversation) \
                .filter(Conversation.is_closed.is_(request_args.is_closed)) \
                .group_by(SecureMessage.thread_id).subquery('t')

            conditions.append(SecureMessage.thread_id == t.c.thread_id)
            conditions.append(SecureMessage.id == t.c.max_id)

            result = SecureMessage.query.filter(and_(*conditions)) \
                .order_by(t.c.max_id.desc()).paginate(request_args.page, request_args.limit, False)

        except SQLAlchemyError:
            logger.exception('Error retrieving messages from database')
            raise InternalServerError(description="Error retrieving messages from database")

        return result

    @staticmethod
    def retrieve_message(message_id, user):
        """returns single message from db"""
        db_model = SecureMessage()
        logger.info("Retrieving message", message_id=message_id)
        try:
            result = db_model.query.filter_by(msg_id=message_id).first()
            if result is None:
                logger.error('Message ID not found', message_id=message_id)
                raise NotFound(description=f"Message with msg_id '{message_id}' does not exist")
        except SQLAlchemyError:
            logger.exception('Error retrieving message from database')
            raise InternalServerError(description="Error retrieving message from database")

        return result.serialize(user)

    @staticmethod
    def retrieve_thread(thread_id, user):
        if user.is_respondent:
            logger.info("Retrieving messages in thread for respondent", thread_id=thread_id, user_uuid=user.user_uuid)
            return Retriever._retrieve_thread_for_respondent(thread_id)
        logger.info("Retrieving messages in thread for internal user", thread_id=thread_id, user_uuid=user.user_uuid)
        return Retriever._retrieve_thread_for_internal_user(thread_id)

    @staticmethod
    def _retrieve_thread_for_respondent(thread_id):
        """returns list of messages for thread id for a respondent"""
        try:
            result = SecureMessage.query.join(Conversation) \
                .filter(SecureMessage.thread_id == thread_id) \
                .order_by(SecureMessage.id.desc())

            if not result.all():
                logger.debug('Thread does not exist', thread_id=thread_id)
                raise NotFound(description=f"Conversation with thread_id '{thread_id}' does not exist")

        except SQLAlchemyError:
            logger.exception('Error retrieving conversation from database')
            raise InternalServerError(description="Error retrieving conversation from database")

        return result

    @staticmethod
    def _retrieve_thread_for_internal_user(thread_id):
        """returns paginated list of messages for thread id for an internal user"""

        try:
            result = SecureMessage.query.join(Events).join(Status) \
                .filter(SecureMessage.thread_id == thread_id) \
                .filter(or_(and_(SecureMessage.from_internal.is_(False), Status.label == Labels.INBOX.value),  # NOQA
                            and_(SecureMessage.from_internal.is_(True),
                                 Status.label.in_([Labels.SENT.value]))
                           )
                       ) \
                .filter(Events.event == EventsApi.SENT.value) \
                .order_by(Status.id.desc())

            if not result.all():
                logger.debug('Thread does not exist', thread_id=thread_id)
                raise NotFound(description=f"Conversation with thread_id '{thread_id}' does not exist")

        except SQLAlchemyError:
            logger.exception('Error retrieving conversation from database')
            raise InternalServerError(description="Error retrieving conversation from database")

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
        except Exception as e:  # NOQA pylint:disable=broad-except
            logger.exception('No connection to database')
            response = jsonify({"status": "unhealthy", "errors": str(e)})
            response.status_code = 500
            return response

        return jsonify({"status": "healthy", "errors": "none"})
