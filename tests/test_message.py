import unittest
import json
import sys
from datetime import datetime, timezone
import app.constants
sys.path.append('../ras-secure-message')
from app.domain_model.domain import Message, MessageSchema


class MessageTestCase(unittest.TestCase):

    maxDiff = None      #Needed as some of the strings are bigger than maxDiff

    def setUp(self):
        self.message = Message(**{'msg_to': 'richard',
                                  'msg_from': 'torrance',
                                  'subject': 'MyMessage',
                                  'body': 'hello',
                                  'thread': "?",
                                  'archived': False,
                                  'marked_as_read': False,
                                  'create_date': datetime.now(timezone.utc),
                                  'read_date': datetime.now(timezone.utc)})

    def testMarshalJson(self):
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(sut.data == self.message)

    def test_message(self):
        now = datetime.now(timezone.utc)
        now_string = now.__str__()
        sut = Message('me', 'you', 'subject', 'body', '5', False, False, now, now)
        sut_str= repr(sut)
        expected = '<Message(msg_to=me msg_from=you subject=subject body=body thread=5 archived=False marked_as_read=False create_date={0} read_date={0})>'.format(now_string)
        self.assertEquals(sut_str, expected)

    def test_message_not_equal(self):
        now = datetime.now(timezone.utc)
        message1 = Message('1', '2', '3', '4', '5', False, False, now, now)
        message2 = Message('1', '33', '3', '4', '5', False, False, now, now)
        self.assertTrue(message1 != message2)

    def test_message_equal(self):
        now = datetime.now(timezone.utc)
        message1 = Message('1', '2', '3', '4', '5', False, False, now, now)
        message2 = Message('1', '2', '3', '4', '5', False, False, now, now)
        self.assertTrue(message1 == message2)

    def test_valid_message_passes_validation(self):
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(sut.errors == {})

    def test_msg_to_field_too_long_fails_validation(self):
        self.message.msg_to = "x"*(app.constants.MAX_TO_LEN + 1)
        expected_error = 'To field length must not be greater than {0}.'.format(app.constants.MAX_TO_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_to'])

    def test_msg_to_min_length_validation_false(self):
        self.message.msg_to = ''
        expected_error = 'To field not populated.'
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_to'])

    def test_msg_missing_to_field_in_Json_causes_error(self):
        message = {'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Missing data for required field.']})

    def test_msg_from_field_too_long_fails_validation(self):
        self.message.msg_from = "x" * (app.constants.MAX_FROM_LEN + 1)
        expected_error = 'From field length must not be greater than {0}.'.format(app.constants.MAX_FROM_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_from'])

    def test_msg_from_min_length_validation_false(self):
        self.message.msg_from = ""
        expected_error = 'From field not populated.'
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_from'])

    def test_msg_from_required_validation_false(self):
        """message marshalling fails msg_from not given"""
        message = {'msg_to': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Missing data for required field.']})

    def test_body_too_big_fails_validation(self):
        self.message.body = "x" * (app.constants.MAX_BODY_LEN + 1)
        expected_error = 'Body field length must not be greater than {0}.'.format(app.constants.MAX_BODY_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['body'])

    def test_missing_body_fails_validation(self):
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': ''}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Body field not populated.']})

    def test_body_field_missing_from_Json_causes_error(self):
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Missing data for required field.']})

    def test_missing_subject_field_does_not_cause_error(self):
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors != {'subject': ['Missing data for required field.']})

    def test_subject_field_too_long_causes_error(self):
        self.message.subject = "x" * (app.constants.MAX_SUBJECT_LEN + 1)
        expected_error = 'Subject field length must not be greater than {0}.'.format(app.constants.MAX_SUBJECT_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['subject'])

    def test_missing_thread_field_does_not_cause_error(self):
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors != {'thread': ['Missing data for required field.']})

    def test_thread_field_too_long_causes_error(self):
        self.message.thread = "x" * (app.constants.MAX_THREAD_LEN + 1)
        expected_error = 'Thread field length must not be greater than {0}.'.format(app.constants.MAX_THREAD_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['thread'])

    def serialise_and_deserialize_message(self):
        schema = MessageSchema()
        json_result = schema.dumps(self.message)
        return schema.load(json.loads(json_result.data))
