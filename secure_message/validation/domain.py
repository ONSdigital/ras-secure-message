import logging
import uuid

from marshmallow import Schema, fields, post_load, validates, ValidationError, pre_load, validates_schema
from flask import g
from structlog import wrap_logger

from secure_message import constants


logger = wrap_logger(logging.getLogger(__name__))


class Message:

    """Class to hold message attributes"""

    def __init__(self, msg_from, subject, body, msg_to='', thread_id=None, msg_id='', collection_case='',
                 survey='', ru_id='', collection_exercise='', from_internal=False):

        self.msg_id = str(uuid.uuid4()) if not msg_id else msg_id  # If empty msg_id assign to a uuid
        self.msg_to = None if not msg_to else msg_to
        self.msg_from = msg_from
        self.subject = subject
        self.body = body
        self.thread_id = self.msg_id if not thread_id else thread_id  # If empty thread_id then set to message id
        self.collection_case = collection_case
        self.ru_id = ru_id
        self.collection_exercise = collection_exercise
        self.survey = survey
        self.from_internal = from_internal

    def __repr__(self):
        return f'<Message(msg_id={self.msg_id} msg_to={self.msg_to} msg_from={self.msg_from} subject={self.subject}' \
               f' body={self.body} thread_id={self.thread_id} collection_case={self.collection_case} ru_id={self.ru_id}' \
               f' collection_exercise={self.collection_exercise} survey={self.survey} from_internal={self.from_internal})>'

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.__dict__ == other.__dict__
        return False


class MessageSchema(Schema):

    """ Class to marshal JSON to Message"""
    msg_id = fields.Str(allow_none=True)
    msg_to = fields.List(fields.String(required=True))
    msg_from = fields.Str(required=True)
    body = fields.Str(required=True)
    subject = fields.Str(required=True)
    thread_id = fields.Str(allow_none=True)
    collection_case = fields.Str(allow_none=True)
    ru_id = fields.Str(required=True)
    survey = fields.Str(required=True)
    collection_exercise = fields.Str(allow_none=True)
    from_internal = fields.Boolean(allow_none=True)

    @pre_load
    def check_sent_and_read_date(self, data):
        self.validate_not_present(data, 'sent_date')
        self.validate_not_present(data, 'read_date')
        return data

    @validates_schema
    def validate_to_from_not_equal(self, data):   # NOQA pylint:disable=no-self-use
        if 'msg_to' in data.keys() and 'msg_from' in data.keys() and data['msg_to'][0] == data['msg_from']:
            logger.error('Message to and message from cannot be the same', message_to=data['msg_to'][0], message_from=data['msg_from'])
            raise ValidationError("msg_to and msg_from fields can not be the same.")

    @validates("msg_to")
    def validate_to(self, msg_to):
        for item in msg_to:
            self.validate_non_zero_field_length("msg_to", len(item), constants.MAX_TO_LEN)
            if g.user.is_internal:  # internal user must be sending to a respondent
                if not g.user.is_valid_respondent(item):
                    logger.error('Not a valid respondent', user=item)
                    raise ValidationError(f"{item} is not a valid respondent.")
            else:  # Respondent sending to internal
                if not (msg_to[0] == constants.NON_SPECIFIC_INTERNAL_USER or g.user.is_valid_internal_user(msg_to[0])):
                    logger.error('Not a valid internal user', user=item)
                    raise ValidationError(f"{item} is not a valid internal user.")

    @validates("msg_from")
    def validate_from(self, msg_from):
        self.validate_non_zero_field_length("msg_from", len(msg_from), constants.MAX_FROM_LEN)

        if msg_from != g.user.user_uuid:
            logger.error('Users can only send messages from themselves',
                         message_from=msg_from, user_uuid=g.user.user_uuid)
            raise ValidationError(f"You are not authorised to send a message on behalf of user or work group {msg_from}")

    @validates("body")
    def validate_body(self, body):
        self.validate_non_zero_field_length("Body", len(body), constants.MAX_BODY_LEN)

    @validates("subject")
    def validate_subject(self, subject):
        self.validate_non_zero_field_length("Subject", len(subject.strip()), constants.MAX_SUBJECT_LEN)

    @validates("thread_id")
    def validate_thread(self, thread_id):
        if thread_id is not None:
            self.validate_field_length("Thread", len(thread_id), constants.MAX_THREAD_LEN)

    @validates("survey")
    def validate_survey(self, survey):
        self.validate_non_zero_field_length("Survey", len(survey), constants.MAX_SURVEY_LEN)

    @validates("ru_id")
    def validate_ru_id(self, ru_id):
        self.validate_non_zero_field_length("ru_id", len(ru_id), constants.MAX_RU_ID_LEN)

    @validates("collection_case")
    def validate_collection_case(self, collection_case):
        self.validate_field_length("collection_case", len(collection_case), constants.MAX_COLLECTION_CASE_LEN)

    @validates("collection_exercise")
    def validate_collection_exercise(self, collection_exercise):
        self.validate_field_length("collection_exercise", len(collection_exercise), constants.MAX_COLLECTION_EXERCISE_LEN)

    @post_load
    def make_message(self, data):  # NOQA pylint:disable=no-self-use
        logger.debug('Build message', data=data)
        return Message(**data)

    @staticmethod
    def validate_not_present(data, field_name):
        if field_name in data.keys():
            logger.error('Field cannot be set', field_name=field_name)
            raise ValidationError(f"{field_name} can not be set")

    def validate_non_zero_field_length(self, field_name, length, max_field_len):
        if length <= 0:
            logger.error('Field not populated', field_name=field_name)
            if field_name == "Body":
                field_name = "message"
            raise ValidationError(f'Please enter a {field_name.lower()}')
        self.validate_field_length(field_name, length, max_field_len)

    @staticmethod
    def validate_field_length(field_name, length, max_field_len, data=None):
        if length > max_field_len:
            logger.error('Field is too large', field_name=field_name, length=length, max_field_len=max_field_len)
            raise ValidationError(f'{field_name} field length must not be greater than {max_field_len}', field_name, [], data)
