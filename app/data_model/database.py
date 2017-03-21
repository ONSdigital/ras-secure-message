from sqlalchemy import Column, String, Integer, Boolean, DateTime
from flask_sqlalchemy import SQLAlchemy
from structlog import get_logger
from app import constants


logger = get_logger()

db = SQLAlchemy()


class Message(db.Model):

    logger.debug("Hit database message")

    __tablename__ = "secure_message"

    id = Column(Integer, primary_key=True)
    msg_to = Column("msg_to", String(constants.MAX_TO_LEN+1))
    msg_from = Column("msg_from", String(constants.MAX_FROM_LEN+1))
    subject = Column("subject", String(constants.MAX_SUBJECT_LEN+1))
    body = Column("body", String(constants.MAX_BODY_LEN+1))
    thread = Column("thread", String(constants.MAX_THREAD_LEN+1))
    archived = Column("archived", Boolean)
    marked_as_read = Column("marked_as_read", Boolean)
    create_date = Column("create_date", DateTime)
    read_date = Column("read_date", DateTime)

    def __init__(self, msg_to, msg_from, subject, body, thread, archived, marked_as_read, create_date, read_date):
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.subject = subject
        self.body = body
        self.thread = thread
        self.archived = archived
        self.marked_as_read = marked_as_read
        self.create_date = create_date
        self.read_date = read_date
