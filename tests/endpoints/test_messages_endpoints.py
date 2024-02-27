import unittest
from unittest.mock import patch

from flask import json
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from secure_message import application, constants
from secure_message.authentication.jwt import encode
from secure_message.exception.exceptions import MessageSaveException
from secure_message.repository import database
from secure_message.repository.database import SecureMessage
from secure_message.services.service_toggles import party

message_modify_url = "http://localhost:5050/messages/modify/"


class TestMessagesEndpoints(unittest.TestCase):
    BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"
    SPECIFIC_INTERNAL_USER = "SpecificInternalUserId"

    def setUp(self):
        """setup test environment"""
        self.app = application.create_app(config="TestConfig")
        self.client = self.app.test_client()
        self.engine = create_engine(self.app.config["SQLALCHEMY_DATABASE_URI"])

        internal_token_data = {
            constants.USER_IDENTIFIER: TestMessagesEndpoints.SPECIFIC_INTERNAL_USER,
            "role": "internal",
        }

        with self.app.app_context():
            internal_signed_jwt = encode(internal_token_data)

        self.internal_user_header = {"Content-Type": "application/json", "Authorization": internal_signed_jwt}

        self.test_message = {
            "msg_to": ["0a7ad740-10d5-4ecb-b7ca-3c0384afb882"],
            "msg_from": TestMessagesEndpoints.SPECIFIC_INTERNAL_USER,
            "subject": "MyMessage",
            "body": "hello",
            "thread_id": "",
            "case_id": "ACollectionCase",
            "exercise_id": "ACollectionExercise",
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "survey_id": self.BRES_SURVEY,
        }

        with self.app.app_context():
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        party.use_mock_service()

    @patch("secure_message.repository.saver.Saver.save_message")
    def test_message_post_raises_message_exception(self, mock_message_save):
        mock_message_save.side_effect = MessageSaveException("Message save failed")
        url = "http://localhost:5050/messages"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertIn("Messages service error".encode(), response.data)

    @patch("secure_message.repository.retriever.Retriever.retrieve_populated_message_object")
    def test_message_patch_retrieval_raises_sql_exception(self, mock_retrieve_message):
        mock_retrieve_message.side_effect = SQLAlchemyError()
        url = "http://localhost:5050/messages/f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        payload = {
            "business_id": "b4db7171-bba1-497c-8343-7d9ddfe19653",
            "survey_id": "02b9c366-7397-42f7-942a-76dc5876d86d",
        }
        response = self.client.patch(url, json=payload, headers=self.internal_user_header)
        self.assertEqual(response.status_code, 500)
        self.assertIn("SQLAlchemyError".encode(), response.data)
        self.assertIn("Messages service error".encode(), response.data)

    @patch("secure_message.repository.modifier.Modifier.patch_message")
    @patch("secure_message.repository.retriever.Retriever.retrieve_populated_message_object")
    def test_message_patch_raises_sql_exception(self, mock_patch_message, mock_retrieve_message):
        mock_retrieve_message.return_value = SecureMessage(
            msg_id="f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            subject="Something else",
            body="test",
            thread_id="6b358b03-2647-48ae-929f-10c1d8b7d1d9",
            case_id="",
            business_id="b4db7171-bba1-497c-8343-7d9ddfe19653",
            exercise_id="",
            survey_id="02b9c366-7397-42f7-942a-76dc5876d86d",
            from_internal=False,
        )
        mock_patch_message.side_effect = SQLAlchemyError()
        url = "http://localhost:5050/messages/f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        response = self.client.patch(url, data=json.dumps({"is_closed": True}), headers=self.internal_user_header)
        self.assertEqual(response.status_code, 500)
        self.assertIn("SQLAlchemyError".encode(), response.data)
        self.assertIn("Messages service error".encode(), response.data)

    @patch("secure_message.repository.retriever.Retriever.retrieve_message")
    @patch("secure_message.repository.modifier.Modifier.add_unread")
    def test_modify_unread_label_raises_sql_exception(self, mock_add_unread, mock_retrieve_message):
        url = f"{message_modify_url}f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        test_message_copy = self.test_message.copy()
        test_message_copy["msg_to"] = ["GROUP"]
        mock_retrieve_message.return_value = test_message_copy
        mock_add_unread.side_effect = SQLAlchemyError()
        data = {"label": "UNREAD", "action": "add"}
        response = self.client.put(url, json=data, headers=self.internal_user_header)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Messages service error".encode(), response.data)

    @patch("secure_message.repository.retriever.Retriever.retrieve_message")
    @patch("secure_message.repository.modifier.Modifier.mark_message_as_read")
    def test_mark_as_read_raises_sql_exception(self, mock_mark_as_read, mock_retrieve_message):
        url = f"{message_modify_url}f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        test_message_copy = self.test_message.copy()
        test_message_copy["msg_to"] = ["GROUP"]
        mock_retrieve_message.return_value = test_message_copy
        mock_mark_as_read.side_effect = SQLAlchemyError()
        data = {"label": "UNREAD", "action": "remove"}
        response = self.client.put(url, json=data, headers=self.internal_user_header)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Messages service error".encode(), response.data)
