import unittest
from datetime import datetime, timezone

from flask import g

from secure_message import constants
from secure_message.services.service_toggles import internal_user_service, party, case_service
from secure_message.validation.domain import Message, MessageSchema
from secure_message.validation.user import User
from secure_message.application import create_app
from secure_message.constants import MAX_SUBJECT_LEN, MAX_BODY_LEN, MAX_THREAD_LEN


class MessageTestCase(unittest.TestCase):
    """Test case for Messages"""

    def setUp(self):
        """setup test environment"""
        self.now = datetime.now(timezone.utc)
        internal_user_service.use_mock_service()
        party.use_mock_service()
        case_service.use_mock_service()

    def test_message(self):
        """creating Message object"""
        sut = Message('from', 'subject', 'body', ['to'], '5', 'AMsgId', 'ACollectionCase',
                      'ASurveyType', 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'CollectionExercise')
        sut_str = repr(sut)
        expected = '<Message(msg_id=AMsgId msg_to=[\'to\'] msg_from=from subject=subject body=body thread_id=5 collection_case=ACollectionCase ' \
                   'ru_id=f1a5e99c-8edf-489a-9c72-6cabe6c387fc collection_exercise=CollectionExercise survey=ASurveyType from_internal=False)>'
        self.assertEquals(sut_str, expected)

    def test_message_with_different_collection_case_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message('1', '2', '3', '4', '5', 'ACollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387f', 'ASurveyType', 'ACollectionExercise')
        message2 = Message('1', '2', '3', '4', '5', 'AnotherCollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387f', 'ASurveyType', 'AnotherCollectionExercise')
        self.assertTrue(message1 != message2)

    def test_message_with_different_collection_exercise_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message('1', '2', '3', '4', '5', 'ACollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ASurveyType', 'ACollectionExercise')
        message2 = Message('1', '2', '3', '4', '5', 'AnotherCollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ASurveyType', 'AnotherCollectionExercise')

        self.assertTrue(message1 != message2)

    def test_message_with_different_ru_id_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message('1', '2', '3', '4', '5', 'ACollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ASurveyType', 'ACollectionExercise')
        message2 = Message('1', '2', '3', '4', '5', 'ACollectionCase',
                           '7fc0e8ab-189c-4794-b8f4-9f05a1db185b', 'ASurveyType', 'AnotherCollectionExercise')

        self.assertTrue(message1 != message2)

    def test_message_with_different_survey_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message('1', '2', '3', '4', '5', 'ACollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ASurveyType', 'ACollectionExercise')
        message2 = Message('1', '2', '3', '4', '5', 'ACollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'AnotherSurveyType', 'AnotherCollectionExercise')

        self.assertTrue(message1 != message2)

    def test_message_equal(self):
        """testing two same Message objects are equal"""
        message1 = Message('1', '2', '3', '4', '5', 'MsgId')
        message2 = Message('1', '2', '3', '4', '5', 'MsgId')
        self.assertTrue(message1 == message2)

    def test_message_not_equal_to_different_type(self):

        message1 = Message('1', '2', '3', '4', '5', 'ACollectionCase',
                           'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ASurveyType')
        self.assertFalse(message1 == "Message1")


class MessageSchemaTestCase(unittest.TestCase):
    """Test case for MessageSchema"""
    def setUp(self):
        """setup test environment"""
        self.json_message = {'msg_to': ['Tej'], 'msg_from': 'Gemma', 'subject': 'MyMessage', 'body': 'hello',
                             'thread_id': "", 'ru_id': "7fc0e8ab-189c-4794-b8f4-9f05a1db185b", 'survey': "RSI"}
        self.now = datetime.now(timezone.utc)
        internal_user_service.use_mock_service()
        party.use_mock_service()
        case_service.use_mock_service()
        self.app = create_app()

    def test_valid_message_passes_validation(self):
        """marshaling a valid message"""
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        schema = MessageSchema()
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            result = schema.load(self.json_message)
        self.assertTrue(result.errors == {})

    def test_valid_domain_message_passes_deserialization(self):
        """checking marshaling message object to json does not raise errors"""
        schema = MessageSchema()
        message_object = Message(**{'msg_to': ['Tej'], 'msg_from': 'Gemma', 'subject': 'MyMessage', 'body': 'hello',
                                    'thread_id': "", 'ru_id': "7fc0e8ab-189c-4794-b8f4-9f05a1db185b"})
        message_json = schema.dumps(message_object)
        self.assertTrue(message_json.errors == {})

    def test_body_too_big_fails_validation(self):
        """marshalling message with body field too long """
        self.json_message['body'] = "x" * (MAX_BODY_LEN + 1)
        expected_error = f"Body field length must not be greater than {MAX_BODY_LEN}"

        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            sut = schema.load(self.json_message)

        self.assertTrue(expected_error in sut.errors['body'])

    def test_missing_body_fails_validation(self):
        """marshalling message with no body field """
        message = {'msg_to': ['01b51fcc-ed43-4cdb-ad1c-450f9986859b'], 'msg_from': 'torrance', 'body': '', 'survey': 'RSI', 'subject': 'MyMessage',
                   'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b'}

        with self.app.app_context():
            g.user = User(message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(message)[1]
        self.assertTrue(errors == {'body': ['Please enter a message']})

    def test_missing_subject_fails_validation(self):
        """marshalling message with no subject field """
        self.json_message.pop('subject', 'MyMessage')
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]
        self.assertTrue(errors == {'subject': ['Missing data for required field.']})

    def test_empty_subject_fails_validation(self):
        """marshalling message with no subject field """
        self.json_message['subject'] = ''
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]
        self.assertTrue(errors == {'subject': ['Please enter a subject']})

    def test_subject_with_only_spaces_fails_validation(self):
        """marshalling message with no subject field """
        self.json_message['subject'] = '  '
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]
        self.assertTrue(errors == {'subject': ['Please enter a subject']})

    def test_subject_field_too_long_causes_error(self):
        """marshalling message with subject field too long"""
        self.json_message['subject'] = "x" * (MAX_SUBJECT_LEN + 1)
        expected_error = f"Subject field length must not be greater than {MAX_SUBJECT_LEN}"
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            sut = schema.load(self.json_message)
        self.assertTrue(expected_error in sut.errors['subject'])

    def test_missing_thread_field_does_not_cause_error(self):
        """marshalling message with no thread_id field"""
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        self.json_message.pop('thread_id', "")
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]
        self.assertTrue(errors == {})

    def test_thread_field_too_long_causes_error(self):
        """marshalling message with thread_id field too long"""
        self.json_message['thread_id'] = "x" * (MAX_THREAD_LEN + 1)
        expected_error = f"Thread field length must not be greater than {MAX_THREAD_LEN}"
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            sut = schema.load(self.json_message)
        self.assertTrue(expected_error in sut.errors['thread_id'])

    def test_missing_msg_id_causes_a_string_the_same_length_as_uuid_to_be_used(self):
        """Missing msg_id causes a uuid is used"""
        self.json_message['msg_id'] = ''
        self.json_message['msg_to'] = ['01b51fcc-ed43-4cdb-ad1c-450f9986859b']
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            sut = schema.load(self.json_message)
        self.assertEquals(len(sut.data.msg_id), 36)

    def test_setting_read_date_field_causes_error(self):
        """marshalling message with no thread_id field"""
        message = {'msg_to': ['torrance'], 'msg_from': 'someone', 'body': 'hello', 'subject': 'subject',
                   'read_date': self.now}

        with self.app.app_context():
            g.user = User(message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(message)[1]

        self.assertTrue(errors == {'_schema': ['read_date can not be set']})

    def test_missing_survey_causes_error(self):
        """marshalling message with no survey field"""
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        self.json_message['survey'] = ''
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]
        self.assertTrue(errors == {'survey': ['Please enter a survey']})

    def test_same_to_from_causes_error(self):
        """marshalling message with same to and from field"""
        self.json_message['msg_from'] = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]

        self.assertTrue(errors == {'_schema': ['msg_to and msg_from fields can not be the same.']})

    def test_msg_to_list_of_string(self):
        """marshalling message where msg_to field is list of strings"""
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]

        self.assertTrue(errors == {})

    def test_msg_to_string(self):
        """marshalling message where msg_to field is string"""
        self.json_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]

        self.assertTrue(errors == {})

    def test_msg_from_string(self):
        """marshalling message where msg_from field is string"""
        self.json_message['msg_to'] = [constants.NON_SPECIFIC_INTERNAL_USER]
        self.json_message['msg_from'] = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
        with self.app.app_context():
            g.user = User(self.json_message['msg_from'], 'respondent')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]

        self.assertTrue(errors == {})

    def test_msg_to_validation_invalid_respondent(self):
        """marshalling message where msg_to field is a invalid user"""
        self.json_message['msg_to'] = ["NotAValidUser"]
        self.json_message['msg_from'] = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
        with self.app.app_context():
            g.user = User("01b51fcc-ed43-4cdb-ad1c-450f9986859b", 'internal')
            schema = MessageSchema()
            errors = schema.load(self.json_message)[1]

        self.assertTrue(errors == {'msg_to': ['NotAValidUser is not a valid respondent.']})


if __name__ == '__main__':
    unittest.main()
