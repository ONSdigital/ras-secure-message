from marshmallow import Schema, fields, post_load, validates, ValidationError, pre_load
import logging
from app import constants
import uuid

logger = logging.getLogger(__name__)


class Message:

    """Class to hold message attributes"""
    def __init__(self, msg_to, msg_from, subject, body, thread_id=None, sent_date=None,
                 read_date=None, msg_id='', collection_case='', reporting_unit='', collection_instrument=''):

        logger.debug("Message Class created {0}, {1}, {2}, {3}".format(msg_to, msg_from, subject, body))
        self.msg_id = str(uuid.uuid4()) if len(msg_id) == 0 else msg_id  # If empty msg_id assign to a uuid
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.subject = subject
        self.body = body
        self.thread_id = self.msg_id if not thread_id else thread_id  # If empty thread_id then set to message id
        self.sent_date = sent_date
        self.read_date = read_date
        self.collection_case = collection_case
        self.reporting_unit = reporting_unit
        self.collection_instrument = collection_instrument

    def __repr__(self):
        return '<Message(msg_id={self.msg_id} to={self.msg_to} msg_from={self.msg_from} subject={self.subject} body={self.body} thread_id={self.thread_id} sent_date={self.sent_date} read_date={self.read_date} collection_case={self.collection_case} reporting_unit={self.reporting_unit} collection_instrument={self.collection_instrument})>'.format(self=self)

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.__dict__ == other.__dict__
        else:
            return False


class MessageSchema(Schema):

    """ Class to marshal JSON to Message"""
    msg_id = fields.Str(allow_none=True)
    msg_to = fields.Str(required=True)
    msg_from = fields.Str(required=True)
    body = fields.Str(required=True)
    subject = fields.Str(allow_none=True)
    thread_id = fields.Str(allow_none=True)
    sent_date = fields.DateTime(allow_none=True)
    read_date = fields.DateTime(allow_none=True)
    collection_case = fields.Str(allow_none=True)
    reporting_unit = fields.Str(allow_none=True)
    collection_instrument = fields.Str(allow_none=True)

    @pre_load
    def check_sent_and_read_date(self, data):
        if 'sent_date' in data.keys():
            raise ValidationError('Field "sent_date" can not be set.')
        elif 'read_date' in data.keys():
            raise ValidationError('Field "read_date" can not be set.')
        else:
            return data

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

    @validates("thread_id")
    def validate_thread(self, thread_id):
        if thread_id is not None:
            self.validate_field_length("Thread", len(thread_id), constants.MAX_THREAD_LEN)

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
