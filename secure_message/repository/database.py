import logging
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
)
from sqlalchemy.orm import relationship
from structlog import wrap_logger

from secure_message import constants
from secure_message.common.labels import Labels

logger = wrap_logger(logging.getLogger(__name__))

metadata = MetaData(schema="securemessage")
db = SQLAlchemy(metadata=metadata)


class SecureMessage(db.Model):
    """Secure messaging database model"""

    __tablename__ = "secure_message"

    id = Column("id", Integer(), primary_key=True)
    msg_id = Column("msg_id", String(constants.MAX_MSG_ID_LEN), unique=True, index=True)
    subject = Column("subject", String(constants.MAX_SUBJECT_LEN + 1))
    body = Column("body", String(constants.MAX_BODY_LEN + 1))
    thread_id = Column("thread_id", String(constants.MAX_THREAD_LEN + 1), ForeignKey("conversation.id"), index=True)
    case_id = Column("case_id", String(constants.MAX_COLLECTION_CASE_LEN + 1))
    business_id = Column("business_id", String(constants.MAX_BUSINESS_ID_LEN + 1))
    exercise_id = Column("exercise_id", String(constants.MAX_COLLECTION_EXERCISE_LEN + 1))
    survey_id = Column("survey_id", String(constants.MAX_SURVEY_LEN + 1))
    from_internal = Column("from_internal", Boolean())
    sent_at = Column("sent_at", DateTime(), default=datetime.utcnow)
    read_at = Column("read_at", DateTime())

    statuses = relationship("Status", backref="secure_message", lazy="dynamic")

    __table_args__ = (Index("idx_ru_survey_cc", "business_id", "survey_id", "case_id", "exercise_id"),)

    def __init__(
        self,
        msg_id="",
        subject="",
        body="",
        thread_id="",
        case_id="",
        business_id="",
        survey_id="",
        exercise_id="",
        from_internal=False,
        read_at=None,
    ):

        logger.debug(f"Initialised Secure Message entity: msg_id: {id}")
        self.msg_id = msg_id
        self.subject = subject
        self.body = body
        self.thread_id = thread_id
        self.case_id = case_id
        self.business_id = business_id
        self.survey_id = survey_id
        self.exercise_id = exercise_id
        self.from_internal = from_internal
        self.read_at = read_at

    def __repr__(self):
        return (
            f"<SecureMessage(msg_id={self.msg_id} subject={self.subject} body={self.body} thread_id={self.thread_id}"
            f" case_id={self.case_id} business_id={self.business_id} exercise_id={self.exercise_id}"
            f" survey_id={self.survey_id} from_internal={self.from_internal} sent_at={self.sent_at} "
            f"read_at={self.read_at})>"
        )

    def set_from_domain_model(self, domain_model):
        """set dbMessage attributes to domain_model attributes"""
        self.msg_id = domain_model.msg_id
        self.subject = domain_model.subject
        self.body = domain_model.body
        self.thread_id = domain_model.thread_id
        self.case_id = domain_model.case_id
        self.business_id = domain_model.business_id
        self.survey_id = domain_model.survey_id
        self.exercise_id = domain_model.exercise_id
        self.from_internal = domain_model.from_internal

    def serialize(self, user, body_summary=False):
        """Return object data in easily serializeable format"""
        message = {
            "msg_to": [],
            "msg_from": "",
            "msg_id": self.msg_id,
            "subject": self.subject,
            "body": self.body[:100] if body_summary else self.body,
            "thread_id": self.thread_id,
            "case_id": self.case_id,
            "business_id": self.business_id,
            "survey_id": self.survey_id,
            "exercise_id": self.exercise_id,
            "from_internal": self.from_internal,
            "sent_date": str(self.sent_at),
            "read_date": str(self.read_at),
            "_links": "",
            "labels": [],
        }

        if user.is_internal:
            self._populate_to_from_and_labels_internal_user(message)
        else:
            self._populate_to_from_and_labels_respondent(user, message)

        return message

    def _populate_to_from_and_labels_internal_user(self, message):
        """populate the labels and to and from if the user is internal"""
        try:
            if message["from_internal"]:
                respondent = [x.actor for x in self.statuses if x.label == Labels.INBOX.value][0]
            else:
                respondent = [x.actor for x in self.statuses if x.label == Labels.SENT.value][0]
        except IndexError:
            logger.error("Could not determine respondent from message", msg_id=message["msg_id"])
            raise
        for row in self.statuses:
            if row.actor != respondent:
                message["labels"].append(row.label)
            self._add_to_and_from(message, row)

    def _populate_to_from_and_labels_respondent(self, user, message):
        """Populate labels and to and from if the user is a respondent"""
        for row in self.statuses:
            if row.actor == user.user_uuid:
                message["labels"].append(row.label)
            self._add_to_and_from(message, row)

    @staticmethod
    def _add_to_and_from(message, row):
        """Populate the message to and from"""
        if row.label == Labels.INBOX.value:
            message["msg_to"].append(row.actor)
        elif row.label == Labels.SENT.value:
            message["msg_from"] = row.actor


class Status(db.Model):
    """Label Assignment table model"""

    __tablename__ = "status"

    id = Column("id", Integer(), primary_key=True)
    label = Column("label", String(constants.MAX_STATUS_LABEL_LEN + 1))
    msg_id = Column("msg_id", String(constants.MAX_MSG_ID_LEN + 1), ForeignKey("secure_message.msg_id"))
    actor = Column("actor", String(constants.MAX_STATUS_ACTOR_LEN + 1))
    __table_args__ = (Index("idx_msg_id_label", "msg_id", "label"),)

    def __init__(self, label="", msg_id="", actor=""):
        self.msg_id = msg_id
        self.actor = actor
        self.label = label

    def set_from_domain_model(self, msg_id, actor, label):
        self.msg_id = msg_id
        self.actor = actor
        self.label = label

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {"msg_id": self.msg_id, "actor": self.actor, "label": self.label}

        return data


class Conversation(db.Model):
    """Conversation table model"""

    __tablename__ = "conversation"

    id = Column("id", String(length=60), primary_key=True, index=True)
    is_closed = Column("is_closed", Boolean())
    closed_by = Column("closed_by", String())
    closed_by_uuid = Column("closed_by_uuid", String(length=60))
    closed_at = Column("closed_at", DateTime())
    category = Column("category", String(length=60), server_default="SURVEY")

    def __init__(self, is_closed=False, closed_by=None, closed_by_uuid=None, closed_at=None, category=None):
        self.is_closed = is_closed
        self.closed_by = closed_by
        self.closed_by_uuid = closed_by_uuid
        self.closed_at = closed_at
        self.category = category
