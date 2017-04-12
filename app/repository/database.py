from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from app import constants
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class SecureMessage(db.Model):
    """Secure messaging database model"""

    __tablename__ = "secure_message"

    id = Column("id", Integer, primary_key=True)
    msg_id = Column("msg_id", String(constants.MAX_MSG_ID_LEN), unique=True)
    subject = Column("subject", String(constants.MAX_SUBJECT_LEN+1))
    body = Column("body", String(constants.MAX_BODY_LEN+1))
    thread_id = Column("thread_id", String(constants.MAX_THREAD_LEN + 1))
    sent_date = Column("sent_date", DateTime)
    read_date = Column("read_date", DateTime)
    collection_case = Column("collection_case", String(constants.MAX_COLLECTION_CASE_LEN+1))
    reporting_unit = Column("reporting_unit", String(constants.MAX_REPORTING_UNIT_LEN+1))
    survey = Column("survey", String(constants.MAX_SURVEY_LEN+1))

    def __init__(self, msg_id="", subject="", body="", thread_id="",
                 sent_date=datetime.now(timezone.utc), read_date=None, collection_case='',
                 reporting_unit='', survey=''):
        logger.debug("Initialised Secure Message entity: msg_id: {}".format(id))
        self.msg_id = msg_id
        self.subject = subject
        self.body = body
        self.thread_id = thread_id
        self.sent_date = sent_date
        self.read_date = read_date
        self.collection_case = collection_case
        self.reporting_unit = reporting_unit
        self.survey = survey

    def set_from_domain_model(self, domain_model):
        """set dbMessage attributes to domain_model attributes"""
        self.msg_id = domain_model.msg_id
        self.subject = domain_model.subject
        self.body = domain_model.body
        self.thread_id = domain_model.thread_id
        self.sent_date = domain_model.sent_date
        self.read_date = domain_model.read_date
        self.collection_case = domain_model.collection_case
        self.reporting_unit = domain_model.reporting_unit
        self.survey = domain_model.survey

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {
            'msg_id': self.msg_id,
            'subject': self.subject,
            'body': self.body,
            'thread_id': self.thread_id,
            'sent_date': self.sent_date,
            'read_date': self.read_date,
            'collection_case': self.collection_case,
            'reporting_unit': self.reporting_unit,
            'survey': self.survey,
            '_links': ''
        }
        return data


class Status(db.Model):
    """Label Assignment table model"""
    __tablename__ = "status"

    id = Column('id', Integer, primary_key=True)
    label = Column('label', String(constants.MAX_STATUS_LABEL_LEN + 1))
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'))
    actor = Column('actor', String(constants.MAX_STATUS_ACTOR_LEN + 1))

    def __init__(self, label='', msg_id='', actor=''):
        self.label = label
        self.msg_id = msg_id
        self.actor = actor

    def set_from_domain_model(self, msg_id, actor, label):
        self.label = label
        self.msg_id = msg_id
        self.actor = actor

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {
            'label': self.label,
            'msg_id': self.msg_id,
            'actor': self.actor
        }
        return data


class InternalSentAudit(db.Model):
    """Label Assignment table model"""
    __tablename__ = "internal_sent_audit"

    id = Column("id", Integer, primary_key=True)
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'))
    internal_user = Column('internal_user', String(constants.MAX_STATUS_ACTOR_LEN + 1))

    def __init__(self, msg_id='', internal_user=''):
        self.msg_id = msg_id
        self.internal_urn = internal_user

    def set_from_domain_model(self, domain_model):
        self.msg_id = domain_model.msg_id
        self.internal_user = domain_model.internal_user

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {
            'msg_id': self.msg_id,
            'internal_user': self.internal_user
        }
        return data
