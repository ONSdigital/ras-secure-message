import logging

from datetime import datetime, timezone
from structlog import wrap_logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Index, MetaData
from sqlalchemy.orm import relationship
from secure_message import constants
from secure_message.common.eventsapi import EventsApi
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
    thread_id = Column("thread_id", String(constants.MAX_THREAD_LEN + 1), index=True)
    collection_case = Column("collection_case", String(constants.MAX_COLLECTION_CASE_LEN + 1))
    ru_id = Column("ru_id", String(constants.MAX_RU_ID_LEN + 1))
    collection_exercise = Column("collection_exercise", String(constants.MAX_COLLECTION_EXERCISE_LEN + 1))
    survey = Column("survey", String(constants.MAX_SURVEY_LEN + 1))
    from_internal = Column('from_internal', Boolean())
    sent_at = Column('sent_at', DateTime())
    read_at = Column('read_at', DateTime())

    statuses = relationship('Status', backref='secure_message', lazy="dynamic")
    events = relationship('Events', backref='secure_message', order_by='Events.date_time', lazy="dynamic")

    __table_args__ = (Index("idx_ru_survey_cc", "ru_id", "survey", "collection_case", "collection_exercise"), )

    def __init__(self, msg_id="", subject="", body="", thread_id="", collection_case='',
                 ru_id='', survey='', collection_exercise='', from_internal=False, read_at=None):

        logger.debug(f"Initialised Secure Message entity: msg_id: {id}")
        self.msg_id = msg_id
        self.subject = subject
        self.body = body
        self.thread_id = thread_id
        self.collection_case = collection_case
        self.ru_id = ru_id
        self.survey = survey
        self.collection_exercise = collection_exercise
        self.from_internal = from_internal
        self.sent_at = datetime.now(timezone.utc)
        self.read_at = read_at

    def set_from_domain_model(self, domain_model):
        """set dbMessage attributes to domain_model attributes"""
        self.msg_id = domain_model.msg_id
        self.subject = domain_model.subject
        self.body = domain_model.body
        self.thread_id = domain_model.thread_id
        self.collection_case = domain_model.collection_case
        self.ru_id = domain_model.ru_id
        self.survey = domain_model.survey
        self.collection_exercise = domain_model.collection_exercise
        self.from_internal = domain_model.from_internal

    def serialize(self, user, body_summary=False):
        """Return object data in easily serializeable format"""
        message = {'msg_to': [],
                   'msg_from': '',
                   'msg_id': self.msg_id,
                   'subject': self.subject,
                   'body': self.body[:100] if body_summary else self.body,
                   'thread_id': self.thread_id,
                   'collection_case': self.collection_case,
                   'ru_id': self.ru_id,
                   'survey': self.survey,
                   'collection_exercise': self.collection_exercise,
                   'from_internal': self.from_internal,
                   '_links': '',
                   'labels': []}

        if user.is_internal:
            self._populate_to_from_and_labels_internal_user(message)
        else:
            self._populate_to_from_and_labels_respondent(user, message)

        self._populate_events(message)

        return message

    def _populate_to_from_and_labels_internal_user(self, message):
        """populate the labels and to and from if the user is internal"""
        try:
            if message['from_internal']:
                respondent = [x.actor for x in self.statuses if x.label == Labels.INBOX.value][0]
            else:
                respondent = [x.actor for x in self.statuses if x.label == Labels.SENT.value][0]
        except IndexError:
            logger.error("Could not determine respondent from message", msg_id=message["msg_id"])
            raise
        for row in self.statuses:
            if row.actor != respondent:
                message['labels'].append(row.label)
            self._add_to_and_from(message, row)

    def _populate_to_from_and_labels_respondent(self, user, message):
        """Populate labels and to and from if the user is a respondent"""
        for row in self.statuses:
            if row.actor == user.user_uuid:
                message['labels'].append(row.label)
            self._add_to_and_from(message, row)

    @staticmethod
    def _add_to_and_from(message, row):
        """Populate the message to and from"""
        if row.label == Labels.INBOX.value:
            message['msg_to'].append(row.actor)
        elif row.label == Labels.SENT.value:
            message['msg_from'] = row.actor

    def _populate_events(self, message):
        for row in self.events:
            if row.event == EventsApi.SENT.value:
                message['sent_date'] = str(row.date_time)
            elif row.event == EventsApi.READ.value:
                message['read_date'] = str(row.date_time)


class Status(db.Model):
    """Label Assignment table model"""
    __tablename__ = "status"

    id = Column('id', Integer(), primary_key=True)
    label = Column('label', String(constants.MAX_STATUS_LABEL_LEN + 1))
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'))
    actor = Column('actor', String(constants.MAX_STATUS_ACTOR_LEN + 1))
    __table_args__ = (Index("idx_msg_id_label", "msg_id", "label"),)

    def __init__(self, label='', msg_id='', actor=''):
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
        data = {'msg_id': self.msg_id,
                'actor': self.actor,
                'label': self.label}

        return data


class Events(db.Model):
    """Events table model"""
    __tablename__ = "events"

    id = Column('id', Integer(), primary_key=True)
    event = Column('event', String(constants.MAX_EVENT_LEN + 1))
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'), index=True)
    date_time = Column('date_time', DateTime())
    __table_args__ = (Index("idx_msg_id_event", "msg_id", "event"),)

    def __init__(self, msg_id='', event=''):
        self.msg_id = msg_id
        self.event = event
        self.date_time = datetime.now(timezone.utc)
