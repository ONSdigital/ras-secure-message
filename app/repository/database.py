import logging
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app import constants
from app.common.labels import Labels
from app.validation.user import User

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class SecureMessage(db.Model):
    """Secure messaging database model"""

    __tablename__ = "secure_message"

    id = Column("id", Integer(), primary_key=True)
    msg_id = Column("msg_id", String(constants.MAX_MSG_ID_LEN), unique=True, index=True)
    subject = Column("subject", String(constants.MAX_SUBJECT_LEN+1))
    body = Column("body", String(constants.MAX_BODY_LEN+1))
    thread_id = Column("thread_id", String(constants.MAX_THREAD_LEN + 1), index=True)
    collection_case = Column("collection_case", String(constants.MAX_COLLECTION_CASE_LEN+1))
    reporting_unit = Column("reporting_unit", String(constants.MAX_REPORTING_UNIT_LEN+1))
    business_name = Column("business_name", String(constants.MAX_BUSINESS_NAME_LEN + 1))
    survey = Column("survey", String(constants.MAX_SURVEY_LEN+1))
    statuses = relationship('Status', backref='secure_message')
    events = relationship('Events', backref='secure_message', order_by='Events.date_time')
    __table_args__ = (Index("idx_ru_survey_cc", "reporting_unit", "survey", "collection_case"), )

    def __init__(self, msg_id="", subject="", body="", thread_id="", collection_case='',
                 reporting_unit='', survey='', business_name=''):
        logger.debug("Initialised Secure Message entity: msg_id: {}".format(id))
        self.msg_id = msg_id
        self.subject = subject
        self.body = body
        self.thread_id = thread_id
        self.collection_case = collection_case
        self.reporting_unit = reporting_unit
        self.business_name = business_name
        self.survey = survey

    def set_from_domain_model(self, domain_model):
        """set dbMessage attributes to domain_model attributes"""
        self.msg_id = domain_model.msg_id
        self.subject = domain_model.subject
        self.body = domain_model.body
        self.thread_id = domain_model.thread_id
        self.collection_case = domain_model.collection_case
        self.reporting_unit = domain_model.reporting_unit
        self.business_name = domain_model.business_name
        self.survey = domain_model.survey

    def serialize(self, user_urn):
        """Return object data in easily serializeable format"""
        message = {
            'urn_to': [],
            'urn_from': '',
            'msg_id': self.msg_id,
            'subject': self.subject,
            'body': self.body,
            'thread_id': self.thread_id,
            'sent_date': 'N/A',
            'read_date': 'N/A',
            'modified_date': 'N/A',
            'collection_case': self.collection_case,
            'reporting_unit': self.reporting_unit,
            'business_name': self.business_name,
            'survey': self.survey,
            '_links': '',
            'labels': []
        }

        if User(user_urn).is_respondent:
            actor = user_urn
        else:
            actor = self.survey

        for row in self.statuses:
            if row.actor == actor:
                message['labels'].append(row.label)

            if row.label == Labels.INBOX.value:
                message['urn_to'].append(row.actor)
            elif row.label == Labels.SENT.value:
                message['urn_from'] = row.actor
            elif row.label == Labels.DRAFT.value:
                message['urn_from'] = row.actor
            elif row.label == Labels.DRAFT_INBOX.value:
                message['urn_to'].append(row.actor)

        for row in self.events:
            if row.event == 'Sent':
                message['sent_date'] = str(row.date_time)
            elif row.event == 'Draft_Saved':
                message['modified_date'] = str(row.date_time)
            elif row.event == 'Read':
                message['read_date'] = str(row.date_time)

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
        data = {
            'msg_id': self.msg_id,
            'actor': self.actor,
            'label': self.label
        }
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
        data = {
            'msg_id': self.msg_id,
            'internal_user': self.internal_user
        }
        return data


class Events(db.Model):
    """Events table model"""
    __tablename__ = "events"

    id = Column('id', Integer(), primary_key=True)
    event = Column('event', String(constants.MAX_EVENT_LEN + 1))
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'), index=True)
    date_time = Column('date_time', DateTime())
    __table_args__ = (Index("idx_msg_id_event", "msg_id", "event"),)

    def __init__(self, date_time=datetime.now(timezone.utc), msg_id='', event=''):
        self.msg_id = msg_id
        self.event = event
        self.date_time = date_time
