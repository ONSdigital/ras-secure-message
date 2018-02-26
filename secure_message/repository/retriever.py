import logging

from structlog import wrap_logger
from flask import jsonify
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, NotFound

from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.database import db, Events, SecureMessage, Status
from secure_message import constants

logger = wrap_logger(logging.getLogger(__name__))


class Retriever:
    """Created when retrieving messages"""

    @staticmethod
    def retrieve_message_list(user, message_args):
        """returns list of messages from db"""

        if user.is_respondent:
            return Retriever._retrieve_message_list_respondent(message_args, user=user)
        return Retriever._retrieve_message_list_internal(message_args)

    @staticmethod
    def _retrieve_message_list_respondent(message_args, user):
        """returns list of messages from db"""
        conditions = []
        status_conditions = [Status.actor == str(user.user_uuid)]

        if message_args.label:
            status_conditions.append(Status.label == message_args.label)
        else:
            status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

        if message_args.ru_id:
            conditions.append(SecureMessage.ru_id == str(message_args.ru_id))

        if message_args.survey:
            conditions.append(SecureMessage.survey == str(message_args.survey))

        if message_args.cc:
            conditions.append(SecureMessage.collection_case == message_args.cc)

        if message_args.ce:
            conditions.append(SecureMessage.collection_exercise == message_args.ce)

        try:
            t = db.session.query(SecureMessage.msg_id, func.max(Events.date_time)  # pylint:disable=no-member
                                 .label('max_date')) \
                .join(Events).join(Status) \
                .filter(and_(*conditions)) \
                .filter(and_(*status_conditions)) \
                .filter(or_(Events.event == EventsApi.SENT.value, Events.event == EventsApi.DRAFT_SAVED.value)) \
                .group_by(SecureMessage.msg_id).subquery('t')

            if message_args.desc:
                order = t.c.max_date.desc()
            else:
                order = t.c.max_date.asc()

            result = SecureMessage.query \
                .filter(SecureMessage.msg_id == t.c.msg_id) \
                .order_by(order).paginate(message_args.page, message_args.limit, False)

        except Exception as e:
            logger.error('Error retrieving messages from database', error=e)
            raise InternalServerError(description="Error retrieving messages from database")

        return result

    @staticmethod
    def _retrieve_message_list_internal(message_args):
        """returns list of messages from db"""
        conditions = []
        status_reject_conditions = []
        valid_statuses = []
        actor_conditions = []

        if message_args.label:
            valid_statuses.append(message_args.label)
            if message_args.label in [Labels.INBOX.value, Labels.ARCHIVE.value, Labels.UNREAD.value]:
                actor_conditions.append(SecureMessage.from_internal == False)  # NOQA pylint:disable=singleton-comparison
            if message_args.label in [Labels.DRAFT.value, Labels.SENT.value]:
                actor_conditions.append(SecureMessage.from_internal == True)  # NOQA pylint:disable=singleton-comparison
        else:
            status_reject_conditions.append(Labels.DRAFT_INBOX.value)
            valid_statuses = [Labels.INBOX.value, Labels.DRAFT.value]
            actor_conditions.append(True)

        if message_args.ru_id:
            conditions.append(SecureMessage.ru_id == str(message_args.ru_id))

        if message_args.survey:
            conditions.append(SecureMessage.survey == str(message_args.survey))

        if message_args.cc:
            conditions.append(SecureMessage.collection_case == str(message_args.cc))

        if message_args.ce:
            conditions.append(SecureMessage.collection_exercise == str(message_args.ce))

        try:
            t = db.session.query(SecureMessage.msg_id, func.max(Events.date_time)  # pylint:disable=no-member  ~ below used to obtain not in
                                 .label('max_date')) \
                .join(Events).join(Status) \
                .filter(and_(*conditions)) \
                .filter(or_(*actor_conditions)) \
                .filter(~Status.label.in_(status_reject_conditions)) \
                .filter(Status.label.in_(valid_statuses)) \
                .filter(or_(Events.event == EventsApi.SENT.value, Events.event == EventsApi.DRAFT_SAVED.value)) \
                .group_by(SecureMessage.msg_id).subquery('t')

            if message_args.desc:
                order = t.c.max_date.desc()
            else:
                order = t.c.max_date.asc()

            result = SecureMessage.query \
                .filter(SecureMessage.msg_id == t.c.msg_id) \
                .order_by(order).paginate(message_args.page, message_args.limit, False)

        except Exception as e:
            logger.exception('Error retrieving messages from database', error=e)
            raise InternalServerError(description="Error retrieving messages from database")

        return result

    @staticmethod
    def unread_message_count(user):
        """Count users unread messages"""
        status_conditions = []
        status_conditions.append(Status.actor == str(user.user_uuid))
        try:
            result = SecureMessage.query.join(Status).filter(and_(*status_conditions)).filter(
                Status.label == 'UNREAD').count()
        except Exception as e:
            logger.exception('Error retrieving count of unread messages from database', error=e)
            raise InternalServerError(description="Error retrieving count of unread messages from database")
        return result

    @staticmethod
    def retrieve_thread_list(user, request_args):
        """returns list of threads from db"""
        status_conditions = []
        conditions = []
        actor_conditions = []

        if user.is_respondent:
            actor_conditions.append(Status.actor == user.user_uuid)
        else:
            actor_conditions.append(Status.actor == user.user_uuid)
            actor_conditions.append(Status.actor == constants.BRES_USER)
            actor_conditions.append(Status.actor == constants.NON_SPECIFIC_INTERNAL_USER)

        status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

        if request_args.ru_id:
            conditions.append(SecureMessage.ru_id == request_args.ru_id)

        if request_args.survey:
            conditions.append(SecureMessage.survey == request_args.survey)

        if request_args.cc:
            conditions.append(SecureMessage.collection_case == request_args.cc)

        if request_args.ce:
            conditions.append(SecureMessage.collection_exercise == request_args.ce)

        try:
            t = db.session.query(SecureMessage.thread_id, func.max(Events.id)  # pylint:disable=no-member
                                 .label('max_id')) \
                .join(Events).join(Status) \
                .filter(and_(*status_conditions)) \
                .filter(or_(*actor_conditions)) \
                .filter(or_(Events.event == EventsApi.SENT.value, Events.event == EventsApi.DRAFT_SAVED.value)) \
                .group_by(SecureMessage.thread_id).subquery('t')

            conditions.append(SecureMessage.thread_id == t.c.thread_id)
            conditions.append(Events.id == t.c.max_id)

            result = SecureMessage.query.join(Events).join(Status) \
                .filter(or_(Events.event == EventsApi.SENT.value, Events.event == EventsApi.DRAFT_SAVED.value)) \
                .filter(and_(*conditions)) \
                .filter(and_(*status_conditions)) \
                .order_by(t.c.max_id.desc()).paginate(request_args.page, request_args.limit, False)

        except Exception as e:
            logger.exception('Error retrieving messages from database', error=e)
            raise InternalServerError(description="Error retrieving messages from database")

        return result

    @staticmethod
    def retrieve_message(message_id, user):
        """returns single message from db"""
        db_model = SecureMessage()

        try:
            result = db_model.query.filter_by(msg_id=message_id).first()
            if result is None:
                logger.error('Message ID not found', message_id=message_id)
                raise NotFound(description="Message with msg_id '{0}' does not exist".format(message_id))
        except SQLAlchemyError as e:
            logger.error('Error retrieving message from database', error=e)
            raise InternalServerError(description="Error retrieving message from database")

        return result.serialize(user)

    @staticmethod
    def retrieve_thread(thread_id, user, message_args):
        """returns paginated list of messages for thread id"""
        status_conditions = []
        actor_conditions = []

        if user.is_respondent:
            actor_conditions.append(Status.actor == str(user.user_uuid))
        else:
            actor_conditions.append(Status.actor == str(user.user_uuid))
            actor_conditions.append(Status.actor == constants.BRES_USER)
            actor_conditions.append(Status.actor == constants.NON_SPECIFIC_INTERNAL_USER)

        status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

        try:

            result = SecureMessage.query.join(Events).join(Status) \
                .filter(SecureMessage.thread_id == thread_id) \
                .filter(and_(*status_conditions)) \
                .filter(or_(*actor_conditions)) \
                .filter(or_(Events.event == EventsApi.SENT.value, Events.event == EventsApi.DRAFT_SAVED.value)) \
                .order_by(Events.date_time.desc()).paginate(message_args.page, message_args.limit, False)

            if not result.items:
                logger.debug('Thread does not exist', thread_id=thread_id)
                raise NotFound(description="Conversation with thread_id '{0}' does not exist".format(thread_id))

        except SQLAlchemyError as e:
            logger.error('Error retrieving conversation from database', error=e)
            raise InternalServerError(description="Error retrieving conversation from database")

        return result

    @staticmethod
    def retrieve_draft(message_id, user):
        """returns single draft from db"""

        try:
            result = SecureMessage.query.filter(SecureMessage.msg_id == message_id) \
                .filter(SecureMessage.statuses.any(Status.label == Labels.DRAFT.value)).first()
            if result is None:
                logger.error('Draft does not exist', message_id=message_id)
                raise NotFound(description="Draft with msg_id '{0}' does not exist".format(message_id))
        except SQLAlchemyError:
            logger.exception("SQLAlchemy error occurred while retrieving draft")
            raise InternalServerError(description="Error retrieving draft from database")

        message = result.serialize(user)

        return message

    @staticmethod
    def check_db_connection():
        """checks if db connection is working"""
        database_status = {"status": "healthy", "errors": "none"}
        resp = jsonify(database_status)
        resp.status_code = 200

        try:
            SecureMessage().query.limit(1).all()
        except Exception as e:  # NOQA pylint:disable=broad-except
            database_status['status'] = "unhealthy"
            database_status['errors'] = str(e)
            resp = jsonify(database_status)
            resp.status_code = 500
            logger.error('No connection to database', status_code=resp.status_code, error=e)

        return resp

    @staticmethod
    def get_draft(draft_id, user):
        """Check msg_id is that of a valid draft and return true/false if no ID is present"""
        try:
            result = SecureMessage.query.filter(SecureMessage.msg_id == draft_id) \
                .filter(SecureMessage.statuses.any(Status.label == Labels.DRAFT.value)).first()
            return result.serialize(user) if result else None
        except Exception as e:
            logger.error('Error retrieving message from database', error=e)
            raise InternalServerError(description="Error retrieving message from database")
