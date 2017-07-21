import logging
from structlog import wrap_logger
from flask import jsonify
from sqlalchemy import and_, case, func, or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, NotFound
from app.common.labels import Labels
from app.repository.database import SecureMessage, Status, Events, db

logger = wrap_logger(logging.getLogger(__name__))


class Retriever:
    """Created when retrieving messages"""
    @staticmethod
    def retrieve_message_list(page, limit, user, ru_id=None, survey=None, cc=None, ce=None, label=None,
                              descend=True):
        """returns list of messages from db"""
        conditions = []
        status_conditions = []

        if user.is_respondent:
            status_conditions.append(Status.actor == str(user.user_uuid))
        else:
            if survey is not None:
                status_conditions.append(Status.actor == str(survey))
            else:
                status_conditions.append(Status.actor == 'BRES')

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
            t = db.session.query(SecureMessage.msg_id, func.max(Events.date_time).label('max_date')) \
                .join(Events).join(Status) \
                .filter(and_(*conditions)) \
                .filter(and_(*status_conditions)) \
                .filter(or_(Events.event == 'Sent', Events.event == 'Draft_Saved')) \
                .group_by(SecureMessage.msg_id).subquery('t')

            if descend:
                result = SecureMessage.query\
                    .filter(SecureMessage.msg_id == t.c.msg_id) \
                    .order_by(t.c.max_date.desc()).paginate(page, limit, False)

            else:
                result = SecureMessage.query \
                    .filter(SecureMessage.msg_id == t.c.msg_id) \
                    .order_by(t.c.max_date.asc()).paginate(page, limit, False)

        except Exception as e:
            logger.error(e)
            raise InternalServerError(description="Error retrieving messages from database")

        return True, result

    @staticmethod
    def retrieve_thread_list(page, limit, user):
        """returns list of threads from db"""
        status_conditions = []
        conditions = []

        if user.is_respondent:
            status_conditions.append(Status.actor == str(user.user_uuid))
        else:
            status_conditions.append(Status.actor == 'BRES')

        status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

        try:
            t = db.session.query(SecureMessage.msg_id, SecureMessage.thread_id, func.max(Events.date_time).label('max_date'))\
                .join(Events).join(Status) \
                .filter(and_(*status_conditions))\
                .filter(or_(Events.event == 'Sent', Events.event == 'Draft_Saved'))\
                .group_by(SecureMessage.thread_id).subquery('t')

            conditions.append(SecureMessage.msg_id == t.c.msg_id)
            conditions.append(Events.date_time == t.c.max_date)
            conditions.append(Events.event != "Read")

            result = SecureMessage.query.join(Events).join(Status) \
                .filter(and_(*conditions)) \
                .order_by(t.c.max_date.desc()).paginate(page, limit, False)

        except Exception as e:
            logger.error(e)
            raise InternalServerError(description="Error retrieving messages from database")

        return True, result

    @staticmethod
    def retrieve_message(message_id, user):
        """returns single message from db"""
        db_model = SecureMessage()

        try:
            result = db_model.query.filter_by(msg_id=message_id).first()
            if result is None:
                raise NotFound(description="Message with msg_id '{0}' does not exist".format(message_id))
        except SQLAlchemyError as e:
            logger.error(e)
            raise InternalServerError(description="Error retrieving message from database")

        message = result.serialize(user)

        return message

    @staticmethod
    def retrieve_thread(thread_id, user, _survey='BRES'):
        """returns list of messages for thread id"""

        status_conditions = []

        if user.is_respondent:
            status_conditions.append(Status.actor == str(user.user_uuid))
        else:
            status_conditions.append(Status.actor == str(_survey))

        status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

        try:
            result = SecureMessage.query.join(Events).join(Status)\
                .filter(SecureMessage.thread_id == thread_id)\
                .filter(and_(*status_conditions))\
                .order_by(case([(Events.event == 'Sent', Events.date_time),
                                (Events.event == 'Draft_Saved', Events.date_time)],
                               else_=0).desc(), Events.event.desc())

            if result.count() == 0:
                raise NotFound(description="Conversation with thread_id '{0}' does not exist".format(thread_id))

        except SQLAlchemyError as e:
            logger.error(e)
            raise InternalServerError(description="Error retrieving conversation from database")

        conversation = []

        for msg in result:
            conversation.append(msg.serialize(user))

        return conversation

    @staticmethod
    def retrieve_draft(message_id, user):
        """returns single draft from db"""

        try:
            result = SecureMessage.query.filter(SecureMessage.msg_id == message_id)\
                .filter(SecureMessage.statuses.any(Status.label == Labels.DRAFT.value)).first()
            if result is None:
                raise NotFound(description="Draft with msg_id '{0}' does not exist".format(message_id))
        except SQLAlchemyError as e:
            logger.error(e)
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
        except Exception as e:
            database_status['status'] = "unhealthy"
            database_status['errors'] = str(e)
            resp = jsonify(database_status)
            resp.status_code = 500

        return resp

    @staticmethod
    def check_msg_id_is_a_draft(draft_id, user):
        """Check msg_id is that of a valid draft and return true/false if no ID is present"""
        try:
            result = SecureMessage.query.filter(SecureMessage.msg_id == draft_id)\
                .filter(SecureMessage.statuses.any(Status.label == Labels.DRAFT.value)).first()
        except Exception as e:
            logger.error(e)
            raise InternalServerError(description="Error retrieving message from database")

        if result is None:
            return False, result
        else:
            return True, result.serialize(user)
