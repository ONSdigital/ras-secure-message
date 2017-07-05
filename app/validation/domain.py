from marshmallow import Schema, fields, post_load, validates, ValidationError, pre_load, validates_schema
import logging
from app import constants
import uuid
from flask import g
from app.validation.user import User

logger = logging.getLogger(__name__)


class Message:

    """Class to hold message attributes"""

    def __init__(self, msg_from, subject, body, msg_to='', thread_id=None, msg_id='', collection_case='',
                 survey='', ru_id='', collection_exercise=''):

        logger.debug("Message Class created {0}, {1}".format(subject, body))
        self.msg_id = str(uuid.uuid4()) if len(msg_id) == 0 else msg_id  # If empty msg_id assign to a uuid
        self.msg_to = None if len(msg_to) == 0 else msg_to
        self.msg_from = msg_from
        self.subject = subject
        self.body = body
        self.thread_id = self.msg_id if not thread_id else thread_id  # If empty thread_id then set to message id
        self.collection_case = collection_case
        self.ru_id = ru_id
        self.collection_exercise = collection_exercise
        self.survey = survey

    def __repr__(self):
        return '<Message(msg_id={self.msg_id} msg_to={self.msg_to} msg_from={self.msg_from} subject={self.subject} body={self.body} thread_id={self.thread_id} collection_case={self.collection_case} ru_id={self.ru_id} collection_exercise={self.collection_exercise} survey={self.survey})>'.format(self=self)

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.__dict__ == other.__dict__
        else:
            return False


class MessageSchema(Schema):

    """ Class to marshal JSON to Message"""
    msg_id = fields.Str(allow_none=True)
    msg_to = fields.Str(required=True)
    # msg_to = fields.List(required=True)
    msg_from = fields.Str(required=True)
    body = fields.Str(required=True)
    subject = fields.Str(required=True)
    thread_id = fields.Str(allow_none=True)
    collection_case = fields.Str(allow_none=True)
    ru_id = fields.Str(required=True)
    survey = fields.Str(required=True)
    collection_exercise = fields.Str(allow_none=True)

    @pre_load
    def check_sent_and_read_date(self, data):
        self.validate_not_present(data, 'sent_date')
        self.validate_not_present(data, 'read_date')
        return data

    @pre_load
    def check_format_of_msg_to_and_msg_from(self, data):

        if data.get('msg_to') and isinstance(data.get('msg_to'), list) and "id" in data.get('msg_to')[0]:
            data['msg_to'] = data['msg_to'][0]['id']
        elif data.get('msg_to') and isinstance(data.get('msg_to'), list) and len(data.get('msg_to')) >= 1:
            if isinstance(data.get('msg_to')[0], str):
                data['msg_to'] = data.get('msg_to')[0]
            else:
                raise ValidationError("'msg_to' is missing an 'id' or incorrect format")

        if data.get('msg_from') and not isinstance(data.get('msg_from'), str) and "id" in data.get('msg_from'):
            data['msg_from'] = data['msg_from']['id']
        elif data.get('msg_from') and not isinstance(data.get('msg_from'), str):
            raise ValidationError("'msg_from' is missing an 'id' or incorrect format")

        return data

    @validates_schema
    def validate_to_from_not_equal(self, data):
        if 'msg_to' in data.keys() and 'msg_from' in data.keys() and data['msg_to'] == data['msg_from']:
            raise ValidationError("msg_to and msg_from fields can not be the same.")

    @validates('msg_to')
    def validate_to(self, msg_to):
        self.validate_non_zero_field_length("msg_to", len(msg_to), constants.MAX_TO_LEN)
        if msg_to != 'BRES' and not User.is_valid_user(msg_to):
            raise ValidationError("{0} is not a valid user.".format(msg_to))

    @validates('msg_from')
    def validate_from(self, msg_from):
        self.validate_non_zero_field_length("msg_from", len(msg_from), constants.MAX_FROM_LEN)
        if g.user.is_internal and msg_from != 'BRES':
            raise ValidationError('You are not authorised to send a message on behalf of user or work group {0}'
                                  .format(msg_from))
        if g.user.is_respondent and msg_from != g.user.user_uuid:
            raise ValidationError('You are not authorised to send a message on behalf of user or work group {0}'
                                  .format(msg_from))

    @validates('body')
    def validate_body(self, body):
        self.validate_non_zero_field_length("Body", len(body), constants.MAX_BODY_LEN)

    @validates('subject')
    def validate_subject(self, subject):
        self.validate_field_length("Subject", len(subject), constants.MAX_SUBJECT_LEN)

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
    def make_message(self, data):
        logger.debug("Build message")
        return Message(**data)

    @staticmethod
    def validate_not_present(data, field_name):
        if field_name in data.keys():
            raise ValidationError("{0} can not be set.".format(field_name))

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


class DraftSchema(Schema):
    """Class to marshal JSON to Draft"""

    msg_id = fields.Str(allow_none=True)
    msg_to = fields.Str(allow_none=True)
    # msg_to = fields.List(allow_none=True)
    msg_from = fields.Str(required=True)
    body = fields.Str(allow_none=True)
    subject = fields.Str(allow_none=True)
    thread_id = fields.Str(allow_none=True)
    collection_case = fields.Str(allow_none=True)
    ru_id = fields.Str(allow_none=True)
    survey = fields.Str(required=True)
    collection_exercise = fields.Str(allow_none=True)

    @pre_load
    def check_variables_set_and_not_set(self, data):
        """Check sent and read date not set and that from and survey are set"""
        if 'msg_from' not in data or len(data['msg_from']) == 0:
            raise ValidationError("{0} Missing".format('msg_from'))
        if 'survey' not in data or len(data['survey']) == 0:
            raise ValidationError("{0} Missing".format('survey'))
        return data

    @pre_load
    def check_format_of_msg_to_and_msg_from(self, data):

        if data.get('msg_to') and isinstance(data.get('msg_to'), list) and len(data.get('msg_to')) > 0\
                and isinstance(data.get('msg_to')[0], dict) and "id" in data.get('msg_to')[0].keys():
                data['msg_to'] = data['msg_to'][0]['id']
        elif 'msg_to' in data.keys() and isinstance(data.get('msg_to'), list) and len(data.get('msg_to')) > 0:
            if isinstance(data.get('msg_to')[0], str):
                data['msg_to'] = data.get('msg_to')[0]
            else:
                raise ValidationError("'msg_to' is missing an 'id' or incorrect format")
        elif 'msg_to' in data.keys() and isinstance(data.get('msg_to'), list) and len(data.get('msg_to')) == 0:
            data.pop('msg_to')

        if data.get('msg_from') and not isinstance(data.get('msg_from'), str) and "id" in data.get('msg_from'):
            data['msg_from'] = data['msg_from']['id']
        elif data.get('msg_from') and not isinstance(data.get('msg_from'), str):
            raise ValidationError("'msg_from' is missing an 'id' or incorrect format")

        return data

    @validates_schema
    def validate_to_from_not_equal(self, data):
        if 'msg_to' in data.keys() and 'msg_from' in data.keys() and data['msg_to'] == data['msg_from']:
            raise ValidationError("msg_to and msg_from fields can not be the same.")

    @validates("msg_to")
    def validate_to(self, msg_to):
        if msg_to is not None:
            self.validate_field_length(msg_to, len(msg_to), constants.MAX_TO_LEN)
            if len(msg_to) > 0 and msg_to != 'BRES' and not User.is_valid_user(msg_to):
                raise ValidationError("{0} is not a valid user.".format(msg_to))

    @validates("msg_from")
    def validate_from(self, msg_from):
        self.validate_field_length(msg_from, len(msg_from), constants.MAX_FROM_LEN)
        if g.user.is_internal and msg_from != 'BRES':
            raise ValidationError('You are not authorised to save a draft on behalf of user or work group {0}'
                                  .format(msg_from))
        if g.user.is_respondent and msg_from != g.user.user_uuid:
            raise ValidationError('You are not authorised to save a draft on behalf of user or work group {0}'
                                  .format(msg_from))

    @validates("body")
    def validate_body(self, body):
        if body is not None:
            self.validate_field_length(body, len(body), constants.MAX_BODY_LEN)

    @validates("subject")
    def validate_subject(self, subject):
        if subject is not None:
            self.validate_field_length(subject, len(subject), constants.MAX_SUBJECT_LEN)

    @validates("thread_id")
    def validate_thread_id(self, thread_id):
        if thread_id is not None:
            self.validate_field_length(thread_id, len(thread_id), constants.MAX_THREAD_LEN)

    @validates("survey")
    def validate_survey(self, survey):
        self.validate_field_length(survey, len(survey), constants.MAX_SURVEY_LEN)

    @validates("collection_case")
    def validate_collection_case(self, collection_case):
        self.validate_field_length("collection_case", len(collection_case), constants.MAX_COLLECTION_CASE_LEN)

    @validates("collection_exercise")
    def validate_collection_exercise(self, collection_exercise):
        self.validate_field_length("collection_exercise", len(collection_exercise),
                                   constants.MAX_COLLECTION_EXERCISE_LEN)

    @validates("ru_id")
    def validate_ru_id(self, ru_id):
        self.validate_field_length("ru_id", len(ru_id), constants.MAX_RU_ID_LEN)

    @post_load
    def make_draft(self, data):
        return Message(**data)

    @staticmethod
    def validate_field_length(field_name, length, max_field_len):
        if length > max_field_len:
            logger.debug("{0} field is too large {1}  max size: {2}".format(field_name, length, max_field_len))
            raise ValidationError('{0} field length must not be greater than {1}.'.format(field_name, max_field_len))
