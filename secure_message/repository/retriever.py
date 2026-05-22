import logging
from collections import defaultdict

from flask import jsonify
from sqlalchemy import and_, func, or_, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError, TimeoutError
from sqlalchemy.orm.exc import NoResultFound
from structlog import wrap_logger
from werkzeug.exceptions import Forbidden, InternalServerError, NotFound

from secure_message.common.labels import Labels
from secure_message.common.utilities import (
    add_users_and_business_details,
    process_paginated_list,
    set_conversation_type_args,
)
from secure_message.constants import NON_SPECIFIC_INTERNAL_USER
from secure_message.repository.database import Conversation, SecureMessage, Status, db

logger = wrap_logger(logging.getLogger(__name__))


LATEST_SM_SQL = """
    INNER JOIN (
        SELECT
            sm.thread_id,
            MAX(sm.id) AS max_id
        FROM securemessage.secure_message sm
        INNER JOIN securemessage.conversation c
            ON c.id = sm.thread_id
        WHERE {conversation_filters}
        GROUP BY sm.thread_id
    ) latest_sm
        ON sm.id = latest_sm.max_id
"""

PAGINATION_SQL = """
ORDER BY sm.msg_id DESC
LIMIT :limit OFFSET :offset
"""


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
        except SQLAlchemyError as e:
            logger.error("Database error when getting unread message count", error=e)
            raise
        except Exception:
            logger.exception("Unknown error when getting unread message count")
            raise InternalServerError(description="Unknown error when getting unread message count")
        return result

    @staticmethod
    def thread_count_by_survey(request_args, user):
        """Count users threads for a specific survey"""

        is_actor_query = Retriever._is_actor_query(request_args)
        filters = Retriever._build_thread_filters(request_args, is_actor_query, user.user_uuid)
        sql = Retriever._build_thread_query(filters, is_count_query=True, is_actor_query=is_actor_query)
        return db.session.execute(text(sql), filters["params"]).scalar()

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
        """Returns list of threads from db"""

        if user.is_respondent:
            return Retriever._retrieve_respondent_thread_list(request_args, user)

        messages = Retriever._retrieve_internal_thread_list(request_args, str(user.user_uuid))
        return add_users_and_business_details(messages) if messages else []

    @staticmethod
    def _is_actor_query(request_args: dict) -> bool:
        """Return whether the request filters by actor."""
        return request_args.my_conversations or request_args.new_respondent_conversations

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
                .paginate(page=request_args.page, per_page=request_args.limit, error_out=False, count=False)
            )

        except SQLAlchemyError:
            logger.exception("Database error when retrieving respondent thread list")
            raise

        return process_paginated_list(result, user)

    @staticmethod
    def _retrieve_internal_thread_list(request_args: dict, user_id: str) -> list[dict]:
        """
        Retrieve a list of internal message threads. Returns the latest message per thread
        filtered by request arguments.
        """

        is_actor_query = Retriever._is_actor_query(request_args)
        filters = Retriever._build_thread_filters(request_args, is_actor_query, user_id)

        params = filters["params"]
        params["limit"] = request_args.limit
        params["offset"] = (request_args.page - 1) * request_args.limit

        sql = Retriever._build_thread_query(filters, is_actor_query=is_actor_query)
        rows = db.session.execute(text(sql), params).mappings().all()

        if not rows:
            return []

        msg_direction_by_msg_id = {r["msg_id"]: r["from_internal"] for r in rows}
        message_participants_map = Retriever._build_message_participants_map(msg_direction_by_msg_id)

        return [
            {
                "msg_id": r["msg_id"],
                "msg_to": message_participants_map[r["msg_id"]]["msg_to"],
                "msg_from": message_participants_map[r["msg_id"]]["msg_from"],
                "subject": r["subject"],
                "body": r["body"][:100],
                "thread_id": r["thread_id"],
                "business_id": r["business_id"],
                "from_internal": r["from_internal"],
                "sent_date": str(r["sent_at"]),
                "labels": message_participants_map[r["msg_id"]]["labels"],
            }
            for r in rows
        ]

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
        except SQLAlchemyError as e:
            if e.__class__ == NoResultFound:
                logger.info("Message ID not found", message_id=message_id)
                raise NotFound(description=f"Message with msg_id '{message_id}' does not exist")
            logger.exception("Error retrieving message from database")
            raise

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
            raise

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
            logger.exception("Database error when retrieving respondent conversation from database")
            raise

        return result.all()

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
            ).all()

            if not result:
                logger.info("Thread not retrieved for internal user", thread_id=thread_id)
                raise NotFound(description=f"Conversation with thread_id {thread_id} not retrieved")

        except SQLAlchemyError:
            logger.exception(
                "Database error when retrieving respondent conversation from database", thread_id=thread_id
            )
            raise

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
        except (OperationalError, TimeoutError) as e:
            logger.exception("Database connection error", errors=str(e))
            response = jsonify({"status": "unhealthy", "errors": "Database connection error"})
            response.status_code = 500
            return response
        except SQLAlchemyError as e:
            logger.exception("Other database error", errors=str(e))
            response = jsonify({"status": "unhealthy", "errors": "Database error"})
            response.status_code = 500
            return response

        return jsonify({"status": "healthy", "errors": "none"})

    @staticmethod
    def _build_thread_filters(request_args: dict, is_actor_query: bool, user_id: str) -> dict:
        """
        Builds SQL filter clauses and query parameters for thread queries.
        """

        conversation_filters = ["c.is_closed IS :is_closed"]
        secure_message_filters = []
        actor_filter = None
        params = {"is_closed": request_args.is_closed}

        if request_args.category:
            conversation_filters.append("c.category = :category")
            params["category"] = request_args.category

        if request_args.surveys:
            secure_message_filters.append("sm.survey_id = ANY(:surveys)")
            params["surveys"] = request_args.surveys

        if request_args.business_id:
            secure_message_filters.append("sm.business_id = :business_id")
            params["business_id"] = request_args.business_id

        if is_actor_query:
            actor = user_id if request_args.my_conversations else NON_SPECIFIC_INTERNAL_USER
            actor_filter = "s.actor = :actor"
            params["actor"] = actor

        return {
            "conversation_filters": conversation_filters,
            "actor_filter": actor_filter,
            "secure_message_filters": secure_message_filters,
            "params": params,
        }

    @staticmethod
    def _build_message_participants_map(msg_direction_by_msg_id: dict) -> dict:
        """
        Builds a map so a message from and to can be derived, read status is also included (internal only)
        """

        status = (
            db.session.query(Status.msg_id, Status.actor, Status.label)
            .filter(Status.msg_id.in_(list(msg_direction_by_msg_id)))
            .all()
        )
        grouped = defaultdict(lambda: {"msg_to": [], "msg_from": "", "labels": []})

        for msg_id, actor, label in status:
            if label == "SENT":
                grouped[msg_id]["msg_from"] = actor
                grouped[msg_id]["labels"].append("SENT")
            elif label == "INBOX":
                grouped[msg_id]["msg_to"].append(actor)
                grouped[msg_id]["labels"].append("INBOX")
            elif label == "UNREAD":
                if not msg_direction_by_msg_id.get(msg_id, True):
                    grouped[msg_id]["labels"].append("UNREAD")

        return grouped

    @staticmethod
    def _build_thread_query(filters: dict, is_count_query: bool = False, is_actor_query: bool = False) -> str:
        """
        Builds the SQL query string for secure message threads. The query can optionally join the status table when
        actor-based filtering is required. By default, a paginated thread query is built. When `is_count_query`
        is True, a count query is returned instead.

        """

        if is_count_query:
            select_sql = "SELECT COUNT(DISTINCT sm.msg_id)"
        else:
            select_sql = """
            SELECT DISTINCT ON (sm.msg_id)
                sm.msg_id,
                sm.subject,
                sm.body,
                sm.thread_id,
                sm.business_id,
                sm.from_internal,
                sm.sent_at
            """

        if is_actor_query:
            from_sql = """
            FROM securemessage.status s
            INNER JOIN securemessage.secure_message sm
                ON sm.msg_id = s.msg_id
            """
        else:
            from_sql = """
            FROM securemessage.secure_message sm
            """

        conversation_filters = (
            " AND ".join(filters["conversation_filters"]) if filters["conversation_filters"] else "TRUE"
        )
        latest_sm_sql = LATEST_SM_SQL.format(conversation_filters=conversation_filters)
        where_clauses = list(filters["secure_message_filters"])

        if is_actor_query:
            where_clauses.append(filters["actor_filter"])

        where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

        sql = f"""
        {select_sql}
        {from_sql}
        {latest_sm_sql}
        WHERE {where_sql}
        """

        if not is_count_query:
            sql += PAGINATION_SQL

        return sql
