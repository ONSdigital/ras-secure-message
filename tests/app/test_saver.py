import datetime
import unittest
import uuid
from unittest import mock

from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from secure_message.application import create_app
from secure_message.exception.exceptions import MessageSaveException
from secure_message.repository import database
from secure_message.repository.database import SecureMessage, db
from secure_message.repository.saver import Saver
from secure_message.validation.domain import Message


class SaverTestCase(unittest.TestCase):
    """Test case for message saving"""

    def setUp(self):
        """setup test environment"""
        app = create_app(config="TestConfig")
        app.testing = True

        self.engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        self.test_message = Message(
            **{"msg_to": "tej", "msg_from": "gemma", "subject": "MyMessage", "body": "hello", "thread_id": ""}
        )
        with app.app_context():
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db
        self.app = app

    def test_save_message_raises_message_save_exception_on_db_error(self):
        """Tests exception is logged if message save fails"""
        with self.app.app_context():
            mock_session = mock.Mock(db.session)
            mock_session.commit.side_effect = SQLAlchemyError("Not Saved")
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_message(self.test_message, mock_session)

    def test_saved_msg_status_and_sent_time_has_been_saved(self):
        """retrieves message status from database"""
        message_status = {"msg_id": "AMsgId", "actor": "Tej"}
        with self.app.app_context():
            with current_app.test_request_context():
                Saver().save_message(SecureMessage(msg_id="AMsgId", thread_id="AMsgId"))
                Saver().save_msg_status(message_status["actor"], message_status["msg_id"], "INBOX, UNREAD")
                result = SecureMessage.query.filter(SecureMessage.msg_id == "AMsgId").one()
                self.assertTrue(isinstance(result.sent_at, datetime.datetime))
                # Test that sent_at timestamp on message is less than 3 seconds old to prove it
                # was only just created
                delta = datetime.datetime.utcnow() - result.sent_at
                self.assertTrue(delta.total_seconds() < 3)

        # This is horrible and barely tests anything... needs to be rewritten to test
        # WHAT statuses are in the database, not just that is literally anything there
        with self.engine.begin() as con:
            request = con.execute(text("SELECT * FROM securemessage.status"))
            for row in request:
                self.assertTrue(row is not None)
            con.close()

    def test_saved_new_thread_creates_entry_in_conversation_table(self):
        """retrieves message status from database"""
        with self.app.app_context():
            random_uuid = str(uuid.uuid4())
            Saver.save_message(SecureMessage(msg_id=random_uuid, thread_id=random_uuid))
            with self.engine.begin() as con:
                request = con.execute(text("SELECT * FROM securemessage.conversation"))
                row = request.fetchone()
                # Newly created record should be mostly empty
                self.assertEqual(row["id"], random_uuid)
                self.assertFalse(row["is_closed"])
                self.assertIsNone(row["closed_by"])
                self.assertIsNone(row["closed_by_uuid"])
                self.assertIsNone(row["closed_at"])
                self.assertTrue(row["category"] is not None)
                con.close()

    def test_save_msg_status_raises_message_save_exception_on_db_error(self):
        """Tests MessageSaveException generated if db commit fails saving message"""
        with self.app.app_context():
            mock_session = mock.Mock(db.session)
            mock_session.commit.side_effect = SQLAlchemyError("Not Saved")
            message_status = {"msg_id": "AMsgId", "actor": "Tej"}
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_status(message_status["actor"], message_status["msg_id"], "INBOX", mock_session)

    def test_saved_msg_id_and_sent_at_has_been_saved(self):
        """retrieves message event from database"""
        with self.app.app_context():
            with current_app.test_request_context():
                Saver().save_message(SecureMessage(msg_id="AMsgId", thread_id="AMsgId"))

        with self.engine.begin() as con:
            request = con.execute(text("SELECT * FROM securemessage.secure_message limit 1"))
            for row in request:
                self.assertTrue(row is not None)
                self.assertTrue(row["msg_id"] == "AMsgId")

                # Just check that sent_at (11th element) is set without checking the value as we don't have it
                self.assertIsInstance(row["sent_at"], datetime.datetime)
                self.assertTrue(row["sent_at"] is not None)
            con.close()

    def test_status_commit_exception_raises_message_save_exception(self):
        """check status commit exception clears the session"""
        message_status = {"msg_id": "AMsgId", "actor": "Tej"}
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_status(message_status["actor"], message_status["msg_id"], "INBOX, UNREAD")

    def test_msg_commit_exception_does_a_rollback(self):
        """check message commit exception clears the session"""
        with self.app.app_context():
            self.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_message(self.test_message)

                self.db.create_all()
                Saver().save_message(self.test_message)

        with self.engine.begin() as con:
            request = con.execute(
                text("SELECT COUNT(securemessage.secure_message.id) FROM securemessage.secure_message")
            )
            for row in request:
                self.assertTrue(row["count"] == 1)
