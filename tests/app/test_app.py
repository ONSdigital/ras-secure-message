import datetime
import unittest
from unittest.mock import patch

from flask import current_app, json
from sqlalchemy import create_engine

from secure_message import application, constants
from secure_message.api_mocks.party_service_mock import PartyServiceMock
from secure_message.authentication.jwt import encode
from secure_message.common.alerts import AlertViaLogging
from secure_message.repository import database
from secure_message.resources.messages import MessageSend
from secure_message.resources.messages import logger as message_logger
from secure_message.services.service_toggles import internal_user_service, party


class AppTestCase(unittest.TestCase):
    """Test case for application endpoints"""

    BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"
    SPECIFIC_INTERNAL_USER = "SpecificInternalUserId"
    SPECIFIC_EXTERNAL_USER = "0a7ad740-10d5-4ecb-b7ca-3c0384afb882"

    def setUp(self):
        """setup test environment"""
        self.app = application.create_app(config="TestConfig")
        self.client = self.app.test_client()
        self.engine = create_engine(self.app.config["SQLALCHEMY_DATABASE_URI"])

        internal_token_data = {constants.USER_IDENTIFIER: AppTestCase.SPECIFIC_INTERNAL_USER, "role": "internal"}

        external_token_data = {
            constants.USER_IDENTIFIER: AppTestCase.SPECIFIC_EXTERNAL_USER,
            "role": "respondent",
            "claims": [{"business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc", "surveys": [AppTestCase.BRES_SURVEY]}],
        }

        with self.app.app_context():
            internal_signed_jwt = encode(internal_token_data)
            external_signed_jwt = encode(external_token_data)

        self.internal_user_header = {"Content-Type": "application/json", "Authorization": internal_signed_jwt}
        self.external_user_header = {"Content-Type": "application/json", "Authorization": external_signed_jwt}

        self.test_message = {
            "msg_to": ["0a7ad740-10d5-4ecb-b7ca-3c0384afb882"],
            "msg_from": AppTestCase.SPECIFIC_INTERNAL_USER,
            "subject": "MyMessage",
            "body": "hello",
            "thread_id": "",
            "case_id": "ACollectionCase",
            "exercise_id": "ACollectionExercise",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": self.BRES_SURVEY,
        }

        with self.app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        party.use_mock_service()
        internal_user_service.use_mock_service()

    def test_that_checks_post_request_is_within_database(self):
        """check messages from messageSend endpoint saved in database correctly"""

        url = "http://localhost:5050/messages"

        data = {
            "msg_to": ["0a7ad740-10d5-4ecb-b7ca-3c0384afb882"],
            "msg_from": AppTestCase.SPECIFIC_INTERNAL_USER,
            "subject": "MyMessage",
            "body": "hello",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": "a-uuid-for-the-survey",
        }

        response = self.client.post(url, data=json.dumps(data), headers=self.internal_user_header)
        self.assertEqual(response.status_code, 201)  # check post has succeeded

        with self.engine.connect() as con:
            db_data = con.execute(
                "SELECT * FROM securemessage.secure_message "
                "WHERE id = (SELECT MAX(id) FROM securemessage.secure_message)"
            )
            self.assertEqual(db_data.rowcount, 1)
            for row in db_data:
                data = {"subject": row["subject"], "body": row["body"]}
                self.assertEqual({"subject": "MyMessage", "body": "hello"}, data)

    def test_post_request_stores_uuid_in_msg_id_if_message_post_called_with_no_msg_id_set(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/messages"

        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        engine = create_engine(self.app.config["DATABASE_URL"], echo=True)
        with engine.connect() as con:
            db_data = con.execute(
                "SELECT * FROM securemessage.secure_message "
                "WHERE id = (SELECT MAX(id) FROM securemessage.secure_message)"
            )
            self.assertEqual(db_data.rowcount, 1)
            for row in db_data:
                self.assertEqual(len(row["msg_id"]), 36)

    def test_thread_patch_without_content_type_in_header_fails(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/threads/f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        header_copy = self.internal_user_header.copy()
        header_copy.pop("Content-Type")
        response = self.client.patch(url, data=json.dumps({"is_closed": True}), headers=header_copy)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.get_data()),
            {"message": 'Request must set accept content type "application/json" in header.'},
        )

    def test_thread_patch_as_external_user_fails(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/threads/f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        response = self.client.patch(url, data=json.dumps({"is_closed": True}), headers=self.external_user_header)
        self.assertEqual(response.status_code, 403)
        error_message = (
            "You don't have the permission to access the requested resource. "
            "It is either read-protected or not readable by the server."
        )
        self.assertEqual(json.loads(response.get_data()), {"message": error_message})

    def test_reply_to_existing_message_has_same_thread_id_and_different_message_id_as_original(self):
        """check a reply gets same thread id as original"""
        # post json message written up in the ui

        url = "http://localhost:5050/messages"

        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)

        # Now read back the message to get the thread ID

        engine = create_engine(self.app.config["DATABASE_URL"], echo=True)
        with engine.connect() as con:
            db_data = con.execute(
                "SELECT * FROM securemessage.secure_message "
                "WHERE id = (SELECT MAX(id) FROM securemessage.secure_message)"
            )
            for row in db_data:
                self.test_message["thread_id"] = row["thread_id"]

        # Now submit a new message as a reply , Message Id empty , thread id same as last one
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)

        # Now read back the two messages
        original_msg_id = original_thread_id = reply_msg_id = reply_thread_id = ""
        with engine.connect() as con:
            request = con.execute("SELECT * FROM securemessage.secure_message ORDER BY id DESC")
            for row in request:
                if row[0] == 1:
                    original_msg_id = row["msg_id"]
                    original_thread_id = row["thread_id"]
                if row[0] == 2:
                    reply_msg_id = row["msg_id"]
                    reply_thread_id = row["thread_id"]

        self.assertTrue(len(original_msg_id) > 0)
        self.assertTrue(len(original_thread_id) > 0)
        self.assertTrue(len(reply_msg_id) > 0)
        self.assertTrue(len(reply_thread_id) > 0)
        self.assertFalse(original_msg_id == reply_msg_id)
        self.assertTrue(original_thread_id == reply_thread_id)
        self.assertTrue(len(original_thread_id) == 36)  # UUID length
        self.assertTrue(len(reply_msg_id) == 36)

    def test_missing_thread_id_does_not_cause_exception(self):
        """posts to message send end point without 'thread_id'"""
        url = "http://localhost:5050/messages"

        test_message = {
            "msg_to": ["0a7ad740-10d5-4ecb-b7ca-3c0384afb882"],
            "msg_from": "ce12b958-2a5f-44f4-a6da-861e59070a31",
            "subject": "MyMessage",
            "body": "hello",
            "case_id": "ACollectionCase",
            "exercise_id": "ACollectionExercise",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": self.BRES_SURVEY,
        }
        try:
            self.client.post(url, data=json.dumps(test_message), headers=self.internal_user_header)
            self.assertTrue(True)  # i.e no exception
        except Exception as e:
            self.fail(f"post raised unexpected exception: {e}")

    def test_message_post_stores_labels_correctly_for_sender_of_message(self):
        """posts to message send end point to ensure labels are saved as expected"""
        url = "http://localhost:5050/messages"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            db_data = con.execute(
                "SELECT * FROM securemessage.status WHERE label='SENT' AND msg_id='{0}' AND actor='{1}'".format(
                    data["msg_id"], self.test_message["survey_id"]
                )
            )
            for row in db_data:
                self.assertTrue(row is not None)

    def test_message_post_stores_events_correctly_for_message(self):
        """posts to message send end point to ensure events are saved as expected"""
        url = "http://localhost:5050/messages"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            db_data = con.execute(f"SELECT * FROM securemessage.secure_message where msg_id='{data['msg_id']}'")
            for row in db_data:
                self.assertTrue(row is not None)
                self.assertTrue(isinstance(row["sent_at"], datetime.datetime))

    def test_message_post_stores_labels_correctly_for_recipient_of_message(self):
        """posts to message send end point to ensure labels are saved as expected"""
        url = "http://localhost:5050/messages"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)
        # dereferencing msg_to for purpose of test
        with self.engine.connect() as con:
            db_data = con.execute(
                "SELECT * FROM securemessage.status WHERE "
                "label='INBOX' OR label='UNREAD' AND msg_id='{0}'"
                " AND actor='{1}'".format(data["msg_id"], self.test_message["msg_to"][0])
            )
            for row in db_data:
                self.assertTrue(row is not None)

    def test_message_post_stores_status_correctly_for_internal_user(self):
        """posts to message send end point to ensure survey is saved for internal user"""
        url = "http://localhost:5050/messages"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            db_data = con.execute(
                "SELECT * FROM securemessage.status WHERE "
                "msg_id='{0}' AND actor='{1}' AND label='SENT'".format(data["msg_id"], self.test_message["survey_id"])
            )
            for row in db_data:
                self.assertTrue(row is not None)

    @patch.object(
        PartyServiceMock,
        "get_user_details",
        return_value=(
            {
                "id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                "firstName": "Bhavana",
                "emailAddress": "example@example.com",
                "lastName": "Lincoln",
                "telephone": "+443069990888",
                "status": "ACTIVE",
                "sampleUnitType": "BI",
            },
            200,
        ),
    )
    @patch.object(AlertViaLogging, "send")
    def test_notify_called(self, mock_alerter, _):
        """Test that Notify is called when sending a new secure message"""

        url = "http://localhost:5050/messages"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertTrue(mock_alerter.called)

    @patch.object(message_logger, "error")
    @patch.object(MessageSend, "_try_send_alert_email", side_effect=Exception("SomethingBad"))
    def test_exception_in_alert_listeners_raises_exception_but_returns_201(self, mock_sender, mock_logger):
        """Test exceptions in alerting do not prevent a response indicating success"""
        url = "http://localhost:5050/messages"
        result = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertTrue(mock_logger.called)
        self.assertTrue(result.status_code == 201)

    @patch.object(
        PartyServiceMock,
        "get_user_details",
        return_value=(
            {
                "id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                "firstName": "Bhavana",
                "lastName": "Lincoln",
                "telephone": "+443069990888",
                "status": "ACTIVE",
                "sampleUnitType": "BI",
            },
            200,
        ),
    )
    @patch.object(AlertViaLogging, "send")
    def test_if_user_has_no_email_address_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is missing no attempt will be made to send email"""

        url = "http://localhost:5050/messages"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)

    @patch.object(
        PartyServiceMock,
        "get_user_details",
        return_value=(
            {
                "id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                "firstName": "Bhavana",
                "emailAddress": "",
                "lastName": "Lincoln",
                "telephone": "+443069990888",
                "status": "ACTIVE",
                "sampleUnitType": "BI",
            },
            200,
        ),
    )
    @patch.object(AlertViaLogging, "send")
    def test_if_user_has_zero_length_email_address_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is zero length no attempt will be made to send email"""

        url = "http://localhost:5050/messages"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)

    @patch.object(
        PartyServiceMock,
        "get_user_details",
        return_value=(
            {
                "id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                "firstName": "Bhavana",
                "emailAddress": "   ",
                "lastName": "Lincoln",
                "telephone": "+443069990888",
                "status": "ACTIVE",
                "sampleUnitType": "BI",
            },
            200,
        ),
    )
    @patch.object(AlertViaLogging, "send")
    def test_if_user_has_only_whitespace_in_email_address_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is zero length no attempt will be made to send email"""

        url = "http://localhost:5050/messages"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)

    @patch.object(PartyServiceMock, "get_user_details", return_value=({"id": "cantFindThis"}, 400))
    @patch.object(AlertViaLogging, "send")
    def test_if_user_unknown_in_party_service_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is zero length no attempt will be made to send email"""

        url = "http://localhost:5050/messages"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)


if __name__ == "__main__":
    unittest.main()
