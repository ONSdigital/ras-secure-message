import unittest
from datetime import datetime, timezone

from flask import current_app, g
from marshmallow.exceptions import ValidationError

from secure_message import constants
from secure_message.application import create_app
from secure_message.constants import MAX_BODY_LEN, MAX_SUBJECT_LEN, MAX_THREAD_LEN
from secure_message.resources.messages import MessageSend
from secure_message.services.service_toggles import internal_user_service, party
from secure_message.validation.domain import Message, MessageSchema
from secure_message.validation.user import User


class MessageTestCase(unittest.TestCase):
    """Test case for Messages"""

    def setUp(self):
        """setup test environment"""
        self.now = datetime.now(timezone.utc)
        internal_user_service.use_mock_service()
        party.use_mock_service()

    def test_message(self):
        """creating Message object"""
        sut = Message(
            "from",
            "subject",
            "body",
            ["to"],
            "5",
            "AMsgId",
            "ACollectionCase",
            "ASurveyType",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "CollectionExercise",
        )
        sut_str = repr(sut)
        expected = (
            "<Message(msg_id=AMsgId msg_to=['to'] msg_from=from subject=subject body=body thread_id=5 "
            "case_id=ACollectionCase business_id=f1a5e99c-8edf-489a-9c72-6cabe6c387fc "
            "exercise_id=CollectionExercise survey_id=ASurveyType from_internal=False category=None)>"
        )
        self.assertEqual(sut_str, expected)

    def test_technical_message(self):
        """creating Message object"""
        sut = Message(
            msg_from="from",
            subject="subject",
            body="body",
            msg_to=["to"],
            thread_id="5",
            msg_id="AMsgId",
            category="TECHNICAL",
        )
        sut_str = repr(sut)
        expected = (
            "<Message(msg_id=AMsgId msg_to=['to'] msg_from=from subject=subject body=body thread_id=5 "
            "case_id= business_id= exercise_id= survey_id= from_internal=False category=TECHNICAL)>"
        )
        self.assertEqual(sut_str, expected)

    def test_misc_message(self):
        """creating Message object"""
        sut = Message(
            msg_from="from",
            subject="subject",
            body="body",
            msg_to=["to"],
            thread_id="5",
            msg_id="AMsgId",
            category="MISC",
        )
        sut_str = repr(sut)
        expected = (
            "<Message(msg_id=AMsgId msg_to=['to'] msg_from=from subject=subject body=body thread_id=5 "
            "case_id= business_id= exercise_id= survey_id= from_internal=False category=MISC)>"
        )
        self.assertEqual(sut_str, expected)

    def test_message_with_different_case_id_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "ACollectionCase",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387f",
            "ASurveyType",
            "ACollectionExercise",
        )
        message2 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "AnotherCollectionCase",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387f",
            "ASurveyType",
            "AnotherCollectionExercise",
        )
        self.assertTrue(message1 != message2)

    def test_message_with_different_exercise_id_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "ACollectionCase",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "ASurveyType",
            "ACollectionExercise",
        )
        message2 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "AnotherCollectionCase",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "ASurveyType",
            "AnotherCollectionExercise",
        )

        self.assertTrue(message1 != message2)

    def test_message_with_different_business_id_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "ACollectionCase",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "ASurveyType",
            "ACollectionExercise",
        )
        message2 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "ACollectionCase",
            "7fc0e8ab-189c-4794-b8f4-9f05a1db185b",
            "ASurveyType",
            "AnotherCollectionExercise",
        )

        self.assertTrue(message1 != message2)

    def test_message_with_different_survey_not_equal(self):
        """testing two different Message objects are not equal"""
        message1 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "ACollectionCase",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "ASurveyType",
            "ACollectionExercise",
        )
        message2 = Message(
            "1",
            "2",
            "3",
            "4",
            "5",
            "ACollectionCase",
            "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "AnotherSurveyType",
            "AnotherCollectionExercise",
        )

        self.assertTrue(message1 != message2)

    def test_message_equal(self):
        """testing two same Message objects are equal"""
        message1 = Message("1", "2", "3", "4", "5", "MsgId")
        message2 = Message("1", "2", "3", "4", "5", "MsgId")
        self.assertTrue(message1 == message2)

    def test_message_not_equal_to_different_type(self):
        message1 = Message(
            "1", "2", "3", "4", "5", "ACollectionCase", "f1a5e99c-8edf-489a-9c72-6cabe6c387fc", "ASurveyType"
        )
        self.assertFalse(message1 == "Message1")


class MessageSchemaTestCase(unittest.TestCase):
    """Test case for MessageSchema"""

    def setUp(self):
        """setup test environment"""
        self.json_message = {
            "msg_to": ["Tej"],
            "msg_from": "Gemma",
            "subject": "MyMessage",
            "body": "hello",
            "thread_id": "",
            "business_id": "7fc0e8ab-189c-4794-b8f4-9f05a1db185b",
            "survey_id": "RSI",
        }
        self.now = datetime.now(timezone.utc)
        internal_user_service.use_mock_service()
        party.use_mock_service()
        self.app = create_app(config="TestConfig")

    def test_valid_message_passes_validation(self):
        """marshaling a valid message"""
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            try:
                MessageSchema().load(self.json_message)
            except ValidationError:
                self.fail("Schema should've been correct and not thrown an error")

    def test_valid_domain_message_passes_deserialization(self):
        """checking marshaling message object to json does not raise errors"""
        message_object = Message(
            **{
                "msg_to": ["Tej"],
                "msg_from": "Gemma",
                "subject": "MyMessage",
                "body": "hello",
                "thread_id": "",
                "business_id": "7fc0e8ab-189c-4794-b8f4-9f05a1db185b",
            }
        )
        try:
            MessageSchema().dumps(message_object)
        except ValidationError:
            self.fail("Schema should've been correct and not thrown an error")

    def test_body_too_big_fails_validation(self):
        """marshalling message with body field too long"""
        self.json_message["body"] = "x" * (MAX_BODY_LEN + 1)

        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                _ = MessageSchema().load(self.json_message)

        self.assertEqual(e.exception.messages, {"body": [f"Body field length must not be greater than {MAX_BODY_LEN}"]})

    def test_missing_body_fails_validation(self):
        """marshalling message with no body field"""
        message = {
            "msg_to": ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"],
            "msg_from": "torrance",
            "body": "",
            "survey_id": "RSI",
            "subject": "MyMessage",
            "business_id": "7fc0e8ab-189c-4794-b8f4-9f05a1db185b",
        }

        with self.app.app_context():
            g.user = User(message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                _ = MessageSchema().load(message)[1]

        self.assertEqual(e.exception.messages, {"body": ["Please enter a message"]})

    def test_missing_subject_fails_validation(self):
        """marshalling message with no subject field"""
        self.json_message.pop("subject", "MyMessage")
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                _ = MessageSchema().load(self.json_message)[1]
        self.assertEqual(e.exception.messages, {"subject": ["Missing data for required field."]})

    def test_empty_subject_fails_validation(self):
        """marshalling message with no subject field"""
        self.json_message["subject"] = ""
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                _ = MessageSchema().load(self.json_message)[1]
        self.assertEqual(e.exception.messages, {"subject": ["Please enter a subject"]})

    def test_subject_with_only_spaces_fails_validation(self):
        """marshalling message with no subject field"""
        self.json_message["subject"] = "  "
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                _ = MessageSchema().load(self.json_message)[1]

        self.assertEqual(e.exception.messages, {"subject": ["Please enter a subject"]})

    def test_subject_field_too_long_causes_error(self):
        """marshalling message with subject field too long"""
        self.json_message["subject"] = "x" * (MAX_SUBJECT_LEN + 1)
        expected_error = f"Subject field length must not be greater than {MAX_SUBJECT_LEN}"
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                _ = MessageSchema().load(self.json_message)

        self.assertEqual(e.exception.messages, {"subject": [expected_error]})

    def test_missing_thread_field_does_not_cause_error(self):
        """marshalling message with no thread_id field"""
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        self.json_message.pop("thread_id", "")
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            try:
                MessageSchema().load(self.json_message)
            except ValidationError:
                self.fail("Schema should've been correct and not thrown an error")

    def test_thread_field_too_long_causes_error(self):
        """marshalling message with thread_id field too long"""
        self.json_message["thread_id"] = "x" * (MAX_THREAD_LEN + 1)
        expected_error = f"Thread field length must not be greater than {MAX_THREAD_LEN}"
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                _ = MessageSchema().load(self.json_message)

        self.assertEqual(e.exception.messages, {"thread_id": [expected_error]})

    def test_missing_msg_id_causes_a_string_the_same_length_as_uuid_to_be_used(self):
        """Missing msg_id causes a uuid is used"""
        self.json_message["msg_id"] = ""
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            output = MessageSchema().load(self.json_message)
        self.assertEqual(len(output.msg_id), 36)

    def test_setting_read_date_field_causes_error(self):
        """marshalling message with no thread_id field"""
        message = {
            "msg_to": ["torrance"],
            "msg_from": "someone",
            "body": "hello",
            "subject": "subject",
            "read_date": self.now,
        }

        with self.app.app_context():
            g.user = User(message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                MessageSchema().load(message)

        self.assertEqual(e.exception.messages, {"_schema": ["read_date can not be set"]})

    def test_missing_survey_causes_error(self):
        """marshalling message with no survey_id field"""
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        self.json_message["survey_id"] = ""
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                MessageSchema().load(self.json_message)
        self.assertEqual(e.exception.messages, {"survey_id": ["Please enter a survey"]})

    def test_same_to_from_causes_error(self):
        """marshalling message with same to and from field"""
        self.json_message["msg_from"] = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            with self.assertRaises(ValidationError) as e:
                MessageSchema().load(self.json_message)

        self.assertTrue(e.exception.messages == {"_schema": ["msg_to and msg_from fields can not be the same."]})

    def test_msg_to_list_of_string(self):
        """marshalling message where msg_to field is list of strings"""
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            try:
                MessageSchema().load(self.json_message)
            except ValidationError:
                self.fail("Schema should've been correct and not thrown an error")

    def test_msg_to_string(self):
        """marshalling message where msg_to field is string"""
        self.json_message["msg_to"] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            try:
                MessageSchema().load(self.json_message)
            except ValidationError:
                self.fail("Schema should've been correct and not thrown an error")

    def test_msg_from_string(self):
        """marshalling message where msg_from field is string"""
        self.json_message["msg_to"] = [constants.NON_SPECIFIC_INTERNAL_USER]
        self.json_message["msg_from"] = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
        with self.app.app_context():
            g.user = User(self.json_message["msg_from"], "respondent")
            try:
                MessageSchema().load(self.json_message)
            except ValidationError:
                self.fail("Schema should've been correct and not thrown an error")

    def test_msg_to_validation_invalid_respondent(self):
        """marshalling message where msg_to field is a invalid user"""
        self.json_message["msg_to"] = ["NotAValidUser"]
        self.json_message["msg_from"] = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
        with self.app.app_context():
            g.user = User("01b51fcc-ed43-4cdb-ad1c-450f9986859b", "internal")
            with self.assertRaises(ValidationError) as e:
                MessageSchema().load(self.json_message)

        self.assertEqual(e.exception.messages, {"msg_to": ["NotAValidUser is not a valid respondent."]})

    def test_message_url_is_created_correctly(self):
        self.threadId = "threadid"
        with self.app.app_context():
            message_send = MessageSend()
            response = message_send._create_message_url(self.threadId)

            self.assertTrue(
                response
                == {
                    "MESSAGE_URL": f'{current_app.config["FRONTSTAGE_URL"]}'
                    f"/secure-message/threads/{self.threadId}#latest-message"
                }
            )


if __name__ == "__main__":
    unittest.main()
