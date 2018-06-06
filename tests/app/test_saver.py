import datetime
import unittest
from unittest import mock

from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from secure_message.common.eventsapi import EventsApi
from secure_message.repository.saver import Saver
from secure_message.repository import database
from secure_message.repository.database import db
from secure_message.application import create_app
from secure_message.exception.exceptions import MessageSaveException
from secure_message.validation.domain import Message
from secure_message.repository.database import SecureMessage


class SaverTestCase(unittest.TestCase):
    """Test case for message saving"""
    def setUp(self):
        """setup test environment"""
        app = create_app()
        app.testing = True

        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        self.test_message = Message(**{'msg_to': 'tej', 'msg_from': 'gemma', 'subject': 'MyMessage',
                                       'body': 'hello', 'thread_id': ""})
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db
        app.config['NOTIFY_CASE_SERVICE'] = '1'
        self.app = app

    def test_save_message_raises_message_save_exception_on_db_error(self):
        """Tests exception is logged if message save fails"""
        mock_session = mock.Mock(db.session)
        mock_session.commit.side_effect = SQLAlchemyError("Not Saved")
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_message(self.test_message, mock_session)

    def test_saved_msg_status_and_sent_time_has_been_saved(self):
        """retrieves message status from database"""
        message_status = {'msg_id': 'AMsgId', 'actor': 'Tej'}
        with self.app.app_context():
            with current_app.test_request_context():
                Saver().save_message(SecureMessage(msg_id='AMsgId'))
                Saver().save_msg_status(message_status['actor'], message_status['msg_id'], 'INBOX, UNREAD')
                result = SecureMessage.query.filter(SecureMessage.msg_id == 'AMsgId').one()
                self.assertTrue(isinstance(result.sent_at, datetime.datetime))
                # Test that sent_at timestamp on message is less than 3 seconds old to prove it
                # was only just created
                delta = datetime.datetime.utcnow() - result.sent_at
                self.assertTrue(delta.total_seconds() < 3)

        # This is horrible and barely tests anything... needs to be rewritten to test
        # WHAT statuses are in the database, not just that is literally anything there
        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM securemessage.status')
            for row in request:
                self.assertTrue(row is not None)

    def test_save_msg_status_raises_message_save_exception_on_db_error(self):
        """Tests MessageSaveException generated if db commit fails saving message"""
        mock_session = mock.Mock(db.session)
        mock_session.commit.side_effect = SQLAlchemyError("Not Saved")
        message_status = {'msg_id': 'AMsgId', 'actor': 'Tej'}
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_status(message_status['actor'], message_status['msg_id'], 'INBOX', mock_session)

    def test_saved_msg_event_has_been_saved(self):
        """retrieves message event from database"""
        message_event = {'msg_id': 'AMsgId', 'event': EventsApi.SENT.value, 'date_time': ''}
        with self.app.app_context():
            with current_app.test_request_context():
                Saver().save_message(SecureMessage(msg_id='AMsgId'))
                Saver().save_msg_event(message_event['msg_id'], message_event['event'])

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM securemessage.events')
            for row in request:
                self.assertTrue(row is not None)
                self.assertTrue(row[1] == message_event['event'])
                self.assertTrue(row[2] == message_event['msg_id'])
                self.assertTrue(row[3] is not None)

    def test_save_event_raises_message_save_exception_on_db_error(self):
        """Tests MessageSaveException generated if db commit fails saving message event"""
        mock_session = mock.Mock(db.session)
        mock_session.commit.side_effect = SQLAlchemyError("Not Saved")

        message_event = {'msg_id': 'AMsgId', 'event': EventsApi.SENT.value, 'date_time': ''}
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_event(message_event['msg_id'], message_event['event'], mock_session)

    def test_status_commit_exception_raises_MessageSaveException(self):
        """check status commit exception clears the session"""
        message_status = {'msg_id': 'AMsgId', 'actor': 'Tej'}
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_status(message_status['actor'], message_status['msg_id'], 'INBOX, UNREAD')

    def test_event_commit_exception_raises_MessageSaveException(self):
        """check event commit exception clears the session"""
        message_event = {'msg_id': 'AMsgId', 'event': EventsApi.SENT.value, 'date_time': ''}
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_event(message_event['msg_id'], message_event['event'])

    def test_msg_commit_exception_does_a_rollback(self):
        """check message commit exception clears the session"""
        with self.app.app_context():
            self.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_message(self.test_message)

                self.db.create_all()
                Saver().save_message(self.test_message)

        with self.engine.connect() as con:
            request = con.execute('SELECT COUNT(securemessage.secure_message.id) FROM securemessage.secure_message')
            for row in request:
                self.assertTrue(row._row[0] == 1)
