from marshmallow import Schema, fields, post_load, validates, ValidationError
from structlog import get_logger
from datetime import datetime, timezone
from app import constants

logger = get_logger()


class Message:

    def __init__(self, msg_to, msg_from, subject, body, thread, archived, marked_as_read,
                 create_date=datetime.now(timezone.utc), read_date=None):

        self.msg_to = msg_to
        self.msg_from = msg_from
        self.subject = subject
        self.body = body
        self.thread = thread
        self.archived = archived
        self.marked_as_read = marked_as_read
        self.create_date = create_date
        self.read_date = read_date

    def __repr__(self):
        return '<Message(msg_to={self.msg_to} msg_from={self.msg_from} subject={self.subject} body={self.body}\
          thread={self.thread} archived={self.archived} marked_as_read={self.marked_as_read}\
          create_date={self.create_date} read_date={self.read_date})>'.format(self=self)

    def __eq__(self, other):
        if isinstance(other, Message):
            if self.msg_to == other.msg_to and\
                self.msg_from == other.msg_from and\
                self.subject == other.subject and\
                self.body == other.body and\
                self.thread == other.thread and\
                self.archived == other.archived and\
                self.marked_as_read == other.marked_as_read and\
                self.create_date.ctime() == other.create_date.ctime() and\
                    self.read_date.ctime() == other.read_date.ctime():
                    return True
            return False
        else:
            return NotImplemented


class MessageSchema(Schema):

    """ Class to marshal JSON to Message"""

    msg_to = fields.Str(required=True)
    msg_from = fields.Str(required=True)
    body = fields.Str(required=True)
    subject = fields.Str(allow_none=True)
    thread = fields.Str(allow_none=True)
    archived = fields.Bool()
    marked_as_read = fields.Bool()
    create_date = fields.DateTime()
    read_date = fields.DateTime()

    @validates('msg_to')
    def validate_to(self, msg_to):
        self.validate_non_zero_field_length("To", len(msg_to), constants.MAX_TO_LEN)

    @validates('msg_from')
    def validate_msg_from(self, msg_from):
        self.validate_non_zero_field_length("From", len(msg_from), constants.MAX_FROM_LEN)

    @validates('body')
    def validate_body(self, body):
        self.validate_non_zero_field_length("Body", len(body), constants.MAX_BODY_LEN)

    @validates('subject')
    def validate_subject(self, subject):
        if subject is not None:
            self.validate_field_length("Subject", len(subject), constants.MAX_SUBJECT_LEN)

    @validates("thread")
    def validate_thread(self, thread):
        if thread is not None:
            self.validate_field_length("Thread", len(thread), constants.MAX_THREAD_LEN)

    @post_load
    def make_message(self, data):
        logger.debug("Build message")

        return Message(**data)

    def validate_non_zero_field_length(self, field_name, length, max_field_len):
        if length <= 0:
            logger.debug("{0} field not populated".format(field_name))
            raise ValidationError('{0} field not populated.'.format(field_name))
        self.validate_field_length(field_name, length, max_field_len)

    @staticmethod
    def validate_field_length(field_name, length, max_field_len):
        if length > max_field_len:
            logger.debug("{0} field is too large {1}  max size: {2}".format(field_name, length, max_field_len))
            raise ValidationError('{0} field length must not be greater than {1}.'.format(field_name, max_field_len))
