import logging

from structlog import wrap_logger
from flask import jsonify
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, NotFound

from secure_message.common.eventsapi import EventsApi
from secure_message.common.labels import Labels
from secure_message.repository.database import Actors, db, Events, SecureMessage, Status
from secure_message import constants

logger = wrap_logger(logging.getLogger(__name__))


class Retriever:
    """Created when retrieving messages"""

    @staticmethod
    def retrieve_message_list(page, limit, user, ru_id=None, survey=None, cc=None, ce=None, label=None, descend=True):
        """returns list of messages from db"""

        if user.is_respondent:
            return Retriever._retrieve_message_list_respondent(page, limit, user=user, ru_id=ru_id, survey=survey,
                                                               cc=cc, ce=ce, label=label, descend=descend)
        return Retriever._retrieve_message_list_internal(page, limit, ru_id=ru_id, survey=survey,
                                                         cc=cc, ce=ce, label=label, descend=descend)

    @staticmethod
    def _retrieve_message_list_respondent(page, limit, user, ru_id, survey, cc, ce, label, descend):
        """returns list of messages from db"""
        conditions = []
        status_conditions = [Status.actor == str(user.user_uuid)]

        if label is not None:
            status_conditions.append(Status.label == str(label))
        else:
            status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

        if ru_id is not None:
            conditions.append(SecureMessage.ru_id == str(ru_id))

        if survey is not None:
            conditions.append(SecureMessage.survey == str(survey))

        if cc is not None:
            conditions.append(SecureMessage.collection_case == str(cc))

        if ce is not None:
            conditions.append(SecureMessage.collection_exercise == str(ce))

        try:
            t = db.session.query(SecureMessage.msg_id, func.max(Events.date_time)  # pylint:disable=no-member
                                 .label('max_date')) \
                .join(Events).join(Status).outerjoin(Actors) \
                .filter(and_(*conditions)) \
                .filter(and_(*status_conditions)) \
                .filter(or_(Events.event == EventsApi.SENT.value, Events.event == EventsApi.DRAFT_SAVED.value)) \
                .group_by(SecureMessage.msg_id).subquery('t')

            if descend:
                order = t.c.max_date.desc()
            else:
                order = t.c.max_date.asc()

            result = SecureMessage.query \
                .filter(SecureMessage.msg_id == t.c.msg_id) \
                .order_by(order).paginate(page, limit, False)

        except Exception as e:
            logger.error('Error retrieving messages from database', error=e)
            raise InternalServerError(description="Error retrieving messages from database")

        return True, result

    @staticmethod
    def _retrieve_message_list_internal(page, limit, ru_id, survey, cc, ce, label, descend):
        """returns list of messages from db"""
        conditions = []
        status_reject_conditions = []
        valid_statuses = []
        actor_conditions = []

        if label is not None:
            valid_statuses.append(label)
            if label in [Labels.INBOX.value, Labels.ARCHIVE.value, Labels.UNREAD.value]:
                actor_conditions.append(Actors.sent_from_internal == False)  # NOQA pylint:disable=singleton-comparison
            if label in [Labels.DRAFT.value, Labels.SENT.value]:
                actor_conditions.append(Actors.sent_from_internal == True)  # NOQA pylint:disable=singleton-comparison
        else:
            status_reject_conditions.append(Labels.DRAFT_INBOX.value)
            valid_statuses = [Labels.INBOX.value, Labels.DRAFT.value]
            actor_conditions.append(True)

        if ru_id is not None:
            conditions.append(SecureMessage.ru_id == str(ru_id))

        if survey is not None:
            conditions.append(SecureMessage.survey == str(survey))

        if cc is not None:
            conditions.append(SecureMessage.collection_case == str(cc))

        if ce is not None:
            conditions.append(SecureMessage.collection_exercise == str(ce))

        try:
            t = db.session.query(SecureMessage.msg_id, func.max(Events.date_time)  # pylint:disable=no-member  ~ below used to obtain not in
                                 .label('max_date')) \
                .join(Events).join(Status).outerjoin(Actors) \
                .filter(and_(*conditions)) \
                .filter(or_(*actor_conditions)) \
                .filter(~Status.label.in_(status_reject_conditions)) \
                .filter(Status.label.in_(valid_statuses)) \
                .filter(or_(Events.event == EventsApi.SENT.value, Events.event == EventsApi.DRAFT_SAVED.value)) \
                .group_by(SecureMessage.msg_id).subquery('t')

            if descend:
                order = t.c.max_date.desc()
            else:
                order = t.c.max_date.asc()

            result = SecureMessage.query \
                .filter(SecureMessage.msg_id == t.c.msg_id) \
                .order_by(order).paginate(page, limit, False)

        except Exception as e:
            logger.exception('Error retrieving messages from database', error=e)
            raise InternalServerError(description="Error retrieving messages from database")

        return True, result

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
    def retrieve_thread_list(page, limit, user):
        """returns list of threads from db"""
        status_conditions = []
        conditions = []
        actor_conditions = []

        if user.is_respondent:
            actor_conditions.append(Status.actor == str(user.user_uuid))
        else:
            actor_conditions.append(Status.actor == str(user.user_uuid))
            actor_conditions.append(Status.actor == constants.BRES_USER)
            actor_conditions.append(Status.actor == constants.NON_SPECIFIC_INTERNAL_USER)

        status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

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
                .order_by(t.c.max_id.desc()).paginate(page, limit, False)

        except Exception as e:
            logger.exception('Error retrieving messages from database', error=e)
            raise InternalServerError(description="Error retrieving messages from database")

        return True, result

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
    def retrieve_thread(thread_id, user, page, limit):
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
                .order_by(Events.date_time.desc()).paginate(page, limit, False)

            if not result.items:
                logger.debug('Thread does not exist', thread_id=thread_id)
                raise NotFound(description="Conversation with thread_id '{0}' does not exist".format(thread_id))

        except SQLAlchemyError as e:
            logger.error('Error retrieving conversation from database', error=e)
            raise InternalServerError(description="Error retrieving conversation from database")

        return True, result

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
    def check_msg_id_is_a_draft(draft_id, user):
        """Check msg_id is that of a valid draft and return true/false if no ID is present"""
        try:
            result = SecureMessage.query.filter(SecureMessage.msg_id == draft_id) \
                .filter(SecureMessage.statuses.any(Status.label == Labels.DRAFT.value)).first()
        except Exception as e:
            logger.error('Error retrieving message from database', error=e)
            raise InternalServerError(description="Error retrieving message from database")

        if result is None:
            return False, result
        return True, result.serialize(user)
