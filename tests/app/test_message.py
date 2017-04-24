import unittest
import app.constants
from datetime import datetime, timezone
from app.validation.domain import Message, MessageSchema


class MessageTestCase(unittest.TestCase):
    """Test case for Messages"""

    def setUp(self):
        """setup test environment"""
        self.now = datetime.now(timezone.utc)

    def test_message(self):
        """creating Message object"""
        now_string = self.now.__str__()
        sut = Message('to', 'from', 'subject', 'body', '5', self.now, self.now, 'AMsgId', 'ACollectionCase',
                      'AReportingUnit', 'ASurveyType')
        sut_str = repr(sut)
        expected = '<Message(msg_id=AMsgId urn_to=to urn_from=from subject=subject body=body thread_id=5 sent_date={0} read_date={0} collection_case=ACollectionCase reporting_unit=AReportingUnit survey=ASurveyType)>'.format(now_string)
        self.assertEquals(sut_str, expected)

    def test_message_with_different_collection_case_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message('1', '2', '3', '4', '5', self.now, self.now, 'ACollectionCase',
                           'AReportingUnit', 'ASurveyType')
        message2 = Message('1', '2', '3', '4', '5', self.now, self.now, 'AnotherCollectionCase',
                           'AReportingUnit', 'ASurveyType')
        self.assertTrue(message1 != message2)

    def test_message_with_different_reporting_unit_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message('1', '2', '3', '4', '5', self.now, self.now, 'ACollectionCase',
                           'AReportingUnit', 'ASurveyType')
        message2 = Message('1', '2', '3', '4', '5', self.now, self.now, 'ACollectionCase',
                           'AnotherReportingUnit', 'ASurveyType')
        self.assertTrue(message1 != message2)

    def test_message_with_different_survey_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message('1', '2', '3', '4', '5', self.now, self.now, 'ACollectionCase',
                           'AReportingUnit', 'ASurveyType')
        message2 = Message('1', '2', '3', '4', '5', self.now, self.now, 'ACollectionCase',
                           'AReportingUnit', 'AnotherSurveyType')
        self.assertTrue(message1 != message2)

    def test_message_equal(self):
        """testing two same Message objects are equal"""
        message1 = Message('1', '2', '3', '4', '5', self.now, self.now, 'MsgId')
        message2 = Message('1', '2', '3', '4', '5', self.now, self.now, 'MsgId')
        self.assertTrue(message1 == message2)

    def test_message_not_equal_to_different_type(self):

        message1 = Message('1', '2', '3', '4', '5', self.now, self.now, 'ACollectionCase',
                           'AReportingUnit', 'ASurveyType')
        self.assertFalse(message1 == "Message1")


class MessageSchemaTestCase(unittest.TestCase):
    """Test case for MessageSchema"""
    def setUp(self):
        """setup test environment"""
        self.json_message = {'urn_to': 'Tej', 'urn_from': 'Gemma', 'subject': 'MyMessage', 'body': 'hello',
                             'thread_id': "", 'survey': "RSI"}
        self.now = datetime.now(timezone.utc)

    def test_valid_message_passes_validation(self):
        """marshaling a valid message"""
        schema = MessageSchema()
        result = schema.load(self.json_message)
        self.assertTrue(result.errors == {})

    def test_valid_domain_message_passes_deserialization(self):
        """checking marshaling message object to json does not raise errors"""
        schema = MessageSchema()
        message_object = Message(**{'urn_to': 'Tej', 'urn_from': 'Gemma', 'subject': 'MyMessage', 'body': 'hello',
                                    'thread_id': "", 'sent_date': datetime.now(timezone.utc),
                                    'read_date': datetime.now(timezone.utc)})
        message_json = schema.dumps(message_object)
        self.assertTrue(message_json.errors == {})
        self.assertTrue('sent_date' in message_json.data)
        self.assertTrue('read_date' in message_json.data)

    def test_body_too_big_fails_validation(self):
        """marshalling message with body field too long """
        self.json_message['body'] = "x" * (app.constants.MAX_BODY_LEN + 1)
        expected_error = 'Body field length must not be greater than {0}.'.format(app.constants.MAX_BODY_LEN)
        schema = MessageSchema()
        sut = schema.load(self.json_message)
        self.assertTrue(expected_error in sut.errors['body'])

    def test_missing_body_fails_validation(self):
        """marshalling message with no body field """
        message = {'urn_to': 'richard', 'urn_from': 'torrance', 'body': '', 'survey': 'RSI'}
        schema = MessageSchema()
        errors = schema.load(message)[1]
        self.assertTrue(errors == {'body': ['Body field not populated.']})

    def test_missing_subject_field_does_not_cause_error(self):
        """marshalling message with no subject field """
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        errors = schema.load(message)[1]
        self.assertTrue(errors != {'subject': ['Missing data for required field.']})

    def test_subject_field_too_long_causes_error(self):
        """marshalling message with subject field too long"""
        self.json_message['subject'] = "x" * (app.constants.MAX_SUBJECT_LEN + 1)
        expected_error = 'Subject field length must not be greater than {0}.'.format(app.constants.MAX_SUBJECT_LEN)
        schema = MessageSchema()
        sut = schema.load(self.json_message)
        self.assertTrue(expected_error in sut.errors['subject'])

    def test_missing_thread_field_does_not_cause_error(self):
        """marshalling message with no thread_id field"""
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        errors = schema.load(message)[1]
        self.assertTrue(errors != {'thread_id': ['Missing data for required field.']})

    def test_thread_field_too_long_causes_error(self):
        """marshalling message with thread_id field too long"""
        self.json_message['thread_id'] = "x" * (app.constants.MAX_THREAD_LEN + 1)
        expected_error = 'Thread field length must not be greater than {0}.'.format(app.constants.MAX_THREAD_LEN)
        schema = MessageSchema()
        sut = schema.load(self.json_message)
        self.assertTrue(expected_error in sut.errors['thread_id'])

    def test_missing_msg_id_causes_a_string_the_same_length_as_uuid_to_be_used(self):
        """Missing msg_id causes a uuid is used"""
        self.json_message['msg_id'] = ''
        schema = MessageSchema()
        sut = schema.load(self.json_message)
        self.assertEquals(len(sut.data.msg_id), 36)

    def test_setting_read_date_field_causes_error(self):
        """marshalling message with no thread_id field"""
        message = {'urn_to': 'torrance', 'urn_from': 'someone', 'body': 'hello', 'subject': 'subject',
                   'read_date': self.now}
        schema = MessageSchema()
        errors = schema.load(message)[1]
        self.assertTrue(errors == {'_schema': ['read_date can not be set.']})

    def test_setting_sent_date_field_causes_error(self):
        """marshalling message with no thread_id field"""
        message = {'urn_to': 'torrance', 'urn_from': 'someone', 'body': 'hello', 'subject': 'subject',
                   'sent_date': self.now}
        schema = MessageSchema()
        errors = schema.load(message)[1]
        self.assertTrue(errors == {'_schema': ['sent_date can not be set.']})

    def test_missing_survey_causes_error(self):
        """marshalling message with no survey field"""
        self.json_message['survey'] = ''
        schema = MessageSchema()
        errors = schema.load(self.json_message)[1]
        self.assertTrue(errors == {'survey': ['Survey field not populated.']})

if __name__ == '__main__':
    unittest.main()
