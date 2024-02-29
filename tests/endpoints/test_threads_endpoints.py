import json
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from secure_message import application, constants
from secure_message.authentication.jwt import encode
from secure_message.repository import database
from secure_message.repository.database import Conversation, SecureMessage


class TestThreadsEndpoints(unittest.TestCase):
    SPECIFIC_INTERNAL_USER = "SpecificInternalUserId"
    SQL_ERROR = '{"detail":"SQLAlchemyError","title":"Thread service error"}'

    def setUp(self):
        self.app = application.create_app(config="TestConfig")
        self.client = self.app.test_client()
        self.engine = create_engine(self.app.config["SQLALCHEMY_DATABASE_URI"])

        internal_token_data = {
            constants.USER_IDENTIFIER: TestThreadsEndpoints.SPECIFIC_INTERNAL_USER,
            "role": "internal",
        }

        with self.app.app_context():
            internal_signed_jwt = encode(internal_token_data)

        self.internal_user_header = {"Content-Type": "application/json", "Authorization": internal_signed_jwt}

        self.conversation = [
            SecureMessage(
                msg_id="59f79039-05ab-4ce1-8354-ab9e7c64d925",
                subject="Something else",
                body="test",
                thread_id="59f79039-05ab-4ce1-8354-ab9e7c64d925",
                case_id="",
                business_id="65c1070f-af33-4c15-a36c-88da9c2d8e4d",
                exercise_id="",
                survey_id="02b9c366-7397-42f7-942a-76dc5876d86d",
                from_internal=False,
                read_at=None,
            )
        ]

        self.open_conversation_metadata = Conversation(
            is_closed=False, closed_by=None, closed_by_uuid=None, closed_at=None, category="SURVEY"
        )

        self.closed_conversation_metadata = Conversation(
            is_closed=True, closed_by=None, closed_by_uuid=None, closed_at=None, category="SURVEY"
        )

        self.serialized_message = {
            "msg_to": ["GROUP"],
            "msg_from": "5b7156d1-202c-4c62-a2af-522cdd68c038",
            "msg_id": "b4f8e3dd-c5f6-4751-811f-36af7313f3f0",
            "subject": "Something else",
            "body": "test",
            "thread_id": "59f79039-05ab-4ce1-8354-ab9e7c64d925",
            "case_id": "",
            "business_id": "65c1070f-af33-4c15-a36c-88da9c2d8e4d",
            "survey_id": "02b9c366-7397-42f7-942a-76dc5876d86d",
            "exercise_id": "",
            "from_internal": False,
            "sent_date": "2024-02-27 16:22:20.586406",
            "read_date": "2024-02-27 16:24:31.314681",
            "_links": "",
            "labels": ["INBOX"],
        }

        with self.app.app_context():
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    @patch("secure_message.repository.retriever.Retriever.retrieve_thread")
    def test_get_thread_retrieval_raises_sql_exception(self, mock_retriever):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_retriever.side_effect = SQLAlchemyError()

        response = self.client.get(url, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertIn("Database error while retrieving message thread".encode(), response.data)

    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    @patch("secure_message.repository.retriever.Retriever.retrieve_thread")
    def test_get_conversation_metadata_retrieval_raises_sql_exception(
        self, mock_retriever, mock_conversation_metadata_retriever
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_retriever.side_effect = self.conversation
        mock_conversation_metadata_retriever.side_effect = SQLAlchemyError()

        response = self.client.get(url, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertIn("Database error while retrieving message thread".encode(), response.data)

    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    def test_patch_thread_conversation_metadata_retrieval_raises_sql_exception(
        self, mock_conversation_metadata_retriever
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_conversation_metadata_retriever.side_effect = SQLAlchemyError()
        payload = {"is_closed": True}

        response = self.client.patch(url, json=payload, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"detail": "SQLAlchemyError", "title": "Database error when modifying thread"},
            json.loads(response.get_data()),
        )

    @patch("secure_message.repository.modifier.Modifier.patch_conversation")
    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    def test_patch_thread_patch_conversation_raises_sql_exception(
        self, mock_conversation_metadata_retriever, mock_patch_conversation
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_conversation_metadata_retriever.return_value = self.open_conversation_metadata
        mock_patch_conversation.side_effect = SQLAlchemyError()
        payload = {"is_closed": True}

        response = self.client.patch(url, json=payload, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"detail": "SQLAlchemyError", "title": "Database error when modifying thread"},
            json.loads(response.get_data()),
        )

    @patch("secure_message.repository.modifier.Modifier.close_conversation")
    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    def test_patch_thread_close_conversation_raises_sql_exception(
        self, mock_conversation_metadata_retriever, mock_close_conversation
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_conversation_metadata_retriever.return_value = self.open_conversation_metadata
        mock_close_conversation.side_effect = SQLAlchemyError()
        payload = {"is_closed": True}

        response = self.client.patch(url, json=payload, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"detail": "SQLAlchemyError", "title": "Database error when modifying thread"},
            json.loads(response.get_data()),
        )

    @patch("secure_message.repository.modifier.Modifier.open_conversation")
    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    def test_patch_thread_open_conversation_raises_sql_exception(
        self, mock_conversation_metadata_retriever, mock_open_conversation
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_conversation_metadata_retriever.return_value = self.closed_conversation_metadata
        mock_open_conversation.side_effect = SQLAlchemyError()
        payload = {"is_closed": False}

        response = self.client.patch(url, json=payload, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"detail": "SQLAlchemyError", "title": "Database error when modifying thread"},
            json.loads(response.get_data()),
        )

    @patch("secure_message.repository.retriever.Retriever.retrieve_thread")
    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    def test_patch_thread_retrieve_thread_raises_sql_exception(
        self, mock_conversation_metadata_retriever, mock_retrieve_thread
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_conversation_metadata_retriever.return_value = self.closed_conversation_metadata
        mock_retrieve_thread.side_effect = SQLAlchemyError()
        payload = {"category": "TECHNICAL"}

        response = self.client.patch(url, json=payload, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"detail": "SQLAlchemyError", "title": "Database error when modifying thread"},
            json.loads(response.get_data()),
        )

    @patch("secure_message.repository.database.SecureMessage.serialize")
    @patch("secure_message.repository.modifier.Modifier.add_unread")
    @patch("secure_message.repository.retriever.Retriever.retrieve_thread")
    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    def test_patch_add_unread_thread_raises_sql_exception(
        self, mock_conversation_metadata_retriever, mock_retrieve_thread, mock_add_unread, mock_serialize
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_conversation_metadata_retriever.return_value = self.closed_conversation_metadata
        mock_retrieve_thread.return_value = self.conversation
        mock_serialize.return_value = self.serialized_message
        mock_add_unread.side_effect = SQLAlchemyError()
        payload = {"category": "TECHNICAL"}

        response = self.client.patch(url, json=payload, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"detail": "SQLAlchemyError", "title": "Database error when modifying thread"}, json.loads(response.data)
        )

    @patch("secure_message.repository.modifier.Modifier.patch_message")
    @patch("secure_message.repository.modifier.Modifier.add_unread")
    @patch("secure_message.repository.database.SecureMessage.serialize")
    @patch("secure_message.repository.retriever.Retriever.retrieve_thread")
    @patch("secure_message.repository.retriever.Retriever.retrieve_conversation_metadata")
    def test_patch_message_thread_raises_sql_exception(
        self,
        mock_conversation_metadata_retriever,
        mock_retrieve_thread,
        mock_serialize,
        mock_add_unread,
        mock_patch_message,
    ):
        url = "http://localhost:5050/threads/59f79039-05ab-4ce1-8354-ab9e7c64d925"
        mock_conversation_metadata_retriever.return_value = self.closed_conversation_metadata
        mock_retrieve_thread.return_value = self.conversation
        mock_serialize.return_value = self.serialized_message
        mock_add_unread.return_value = None
        mock_patch_message.side_effect = SQLAlchemyError
        payload = {"category": "TECHNICAL"}

        response = self.client.patch(url, json=payload, headers=self.internal_user_header)

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {"detail": "SQLAlchemyError", "title": "Database error when modifying thread"},
            json.loads(response.get_data()),
        )
