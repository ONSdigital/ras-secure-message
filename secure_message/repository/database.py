import logging

from datetime import datetime, timezone
from structlog import wrap_logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Index, MetaData
from sqlalchemy.orm import relationship
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
    thread_id = Column("thread_id", String(constants.MAX_THREAD_LEN + 1), index=True)
    collection_case = Column("collection_case", String(constants.MAX_COLLECTION_CASE_LEN + 1))
    ru_id = Column("ru_id", String(constants.MAX_RU_ID_LEN + 1))
    collection_exercise = Column("collection_exercise", String(constants.MAX_COLLECTION_EXERCISE_LEN + 1))
    survey = Column("survey", String(constants.MAX_SURVEY_LEN + 1))
    statuses = relationship('Status', backref='secure_message', lazy="dynamic")
    events = relationship('Events', backref='secure_message', order_by='Events.date_time', lazy="dynamic")
    actors = relationship('Actors', backref='secure_message', lazy="dynamic")

    __table_args__ = (Index("idx_ru_survey_cc", "ru_id", "survey", "collection_case", "collection_exercise"), )

    def __init__(self, msg_id="", subject="", body="", thread_id="", collection_case='',
                 ru_id='', survey='', collection_exercise=''):

        logger.debug("Initialised Secure Message entity: msg_id: {}".format(id))
        self.msg_id = msg_id
        self.subject = subject
        self.body = body
        self.thread_id = thread_id
        self.collection_case = collection_case
        self.ru_id = ru_id
        self.survey = survey
        self.collection_exercise = collection_exercise

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

    def serialize(self, user, body_summary=False):  # pylint:disable=too-complex, too-many-branches
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
                   '_links': '',
                   'labels': []}

        if user.is_internal:
            actor = constants.BRES_USER
        else:
            actor = user.user_uuid

        for row in self.statuses:
            if row.actor == actor:
                message['labels'].append(row.label)

            if row.label == Labels.INBOX.value:
                message['msg_to'].append(row.actor)
            elif row.label == Labels.SENT.value:
                message['msg_from'] = row.actor
            elif row.label == Labels.DRAFT.value:
                message['msg_from'] = row.actor
            elif row.label == Labels.DRAFT_INBOX.value:
                message['msg_to'].append(row.actor)

        for row in self.events:
            if row.event == 'Sent':
                message['sent_date'] = str(row.date_time)
            elif row.event == 'Draft_Saved':
                message['modified_date'] = str(row.date_time)
            elif row.event == 'Read':
                message['read_date'] = str(row.date_time)

        for row in self.actors:
            message['sent_from_internal'] = row.sent_from_internal

        return message


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


class InternalSentAudit(db.Model):
    """Label Assignment table model"""
    __tablename__ = "internal_sent_audit"

    id = Column("id", Integer(), primary_key=True)
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'), index=True)
    internal_user = Column('internal_user', String(constants.MAX_STATUS_ACTOR_LEN + 1))

    def __init__(self, msg_id='', internal_user=''):
        self.msg_id = msg_id
        self.internal_urn = internal_user

    def set_from_domain_model(self, msg_id, msg_urn):
        """Set internal sent audit table me"""
        self.msg_id = msg_id
        self.internal_user = msg_urn

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {'msg_id': self.msg_id,
                'internal_user': self.internal_user}

        return data


class Actors(db.Model):
    """Label Assignment table model"""
    __tablename__ = "actors"

    id = Column("id", Integer(), primary_key=True)
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'), index=True)
    from_actor = Column('from_actor', String(constants.MAX_STATUS_ACTOR_LEN + 1))
    to_actor = Column('to_actor', String(constants.MAX_STATUS_ACTOR_LEN + 1))
    sent_from_internal = Column('sent_from_internal', Boolean())

    def __init__(self, msg_id, from_actor, to_actor, sent_from_internal):
        self.set_from_domain_model(msg_id, from_actor, to_actor, sent_from_internal)

    def set_from_domain_model(self, msg_id, from_actor, to_actor, sent_from_internal):
        """Set actors values"""
        self.msg_id = msg_id
        self.from_actor = from_actor
        self.to_actor = to_actor
        self.sent_from_internal = sent_from_internal

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {'msg_id': self.msg_id,
                'from_actor': self.from_actor,
                'to_actor': self.to_actor,
                'sent_from_internal': self.sent_from_internal}

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
