from sqlalchemy import Column, String, Integer, Boolean, DateTime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from app import constants
import logging
import uuid

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class DbMessage(db.Model):
    """Secure messaging datasbase model"""
    logger.debug("Hit database message")

    __tablename__ = "secure_message"

    id = Column(Integer, primary_key=True)
    msg_id = Column("msg_id", String(constants.MAX_MSG_ID_LEN))
    msg_to = Column("msg_to", String(constants.MAX_TO_LEN+1))
    msg_from = Column("msg_from", String(constants.MAX_FROM_LEN+1))
    subject = Column("subject", String(constants.MAX_SUBJECT_LEN+1))
    body = Column("body", String(constants.MAX_BODY_LEN+1))
    thread = Column("thread", String(constants.MAX_THREAD_LEN+1))
    archived = Column("archived", Boolean)
    marked_as_read = Column("marked_as_read", Boolean)
    create_date = Column("create_date", DateTime)
    read_date = Column("read_date", DateTime)

    def __init__(self, msg_id="", msg_to="", msg_from="", subject="", body="", thread="", archived=False, marked_as_read=False,
                 create_date=datetime.now(timezone.utc), read_date=None):
        self.msg_id = msg_id
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.subject = subject
        self.body = body
        self.thread = thread
        self.archived = archived
        self.marked_as_read = marked_as_read
        self.create_date = create_date
        self.read_date = read_date

    def set_from_domain_model(self, domain_model):
        """set dbMessage attributes to domain_model attributes"""
        self.msg_id = domain_model.msg_id
        self.msg_to = domain_model.msg_to
        self.msg_from = domain_model.msg_from
        self.subject = domain_model.subject
        self.body = domain_model.body
        self.thread = domain_model.thread
        self.archived = domain_model.archived
        self.marked_as_read = domain_model.marked_as_read
        self.create_date = domain_model.create_date
        self.read_date = domain_model.read_date

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        data = {
           'id': self.id,
           'msg_id': self.msg_id,
           'msg_to': self.msg_to,
           'msg_from': self.msg_from,
           'subject': self.subject,
           'body': self.body,
           'thread': self.thread,
           'archived': self.archived,
           'marked_as_read': self.marked_as_read,
           'create_date': self.create_date,
           'read_date': self.read_date
        }
        return data
