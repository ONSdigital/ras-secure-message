import unittest
from app.repository.saver import Saver
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from app.repository import database
from app.repository.database import db
from flask import current_app
from app.application import app
from unittest import mock
from app.exception.exceptions import MessageSaveException
from app.validation.domain import Message
from app.repository.database import SecureMessage


class SaverTestCase(unittest.TestCase):
    """Test case for message saving"""
    def setUp(self):
        """setup test environment"""
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')
        self.test_message = Message(**{'msg_to': 'tej', 'msg_from': 'gemma', 'subject': 'MyMessage',
                                    'body': 'hello', 'thread_id': ""})
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """enable foreign key constraint for tests"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def test_save_message_raises_message_save_exception_on_db_error(self):
        """Tests exception is logged if message save fails"""
        mock_session = mock.Mock(db.session)
        mock_session.commit.side_effect = Exception("Not Saved")
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_message(self.test_message, mock_session)

    def test_saved_msg_status_has_been_saved(self):
        """retrieves message status from database"""
        message_status = {'msg_id': 'AMsgId', 'actor': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                Saver().save_message(SecureMessage(msg_id='AMsgId'))
                Saver().save_msg_status(message_status['actor'], message_status['msg_id'],  'INBOX, UNREAD')

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM status')
            for row in request:
                self.assertTrue(row is not None)

    def test_save_msg_status_raises_message_save_exception_on_db_error(self):
        """Tests MessageSaveException generated if db commit fails saving message"""
        mock_session = mock.Mock(db.session)
        mock_session.commit.side_effect = Exception("Not Saved")
        message_status = {'msg_id': 'AMsgId', 'actor': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_status(message_status['actor'], message_status['msg_id'], 'INBOX', mock_session)

    def test_save_msg_audit_does_not_raise_exception_on_successful_save(self):
        """Tests message audit is saved to database"""
        message_audit = {'msg_id': 'MsgId', 'msg_urn': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                Saver().save_message(SecureMessage(msg_id='MsgId'))
                Saver().save_msg_audit(message_audit['msg_id'], message_audit['msg_urn'])
                self.assertTrue(True)

    def test_save_msg_audit_raises_message_save_exception_on_db_error(self):
        """Tests MessageSaveException generated if db commit fails saving message audit"""
        mock_session = mock.Mock(db.session)
        mock_session.commit.side_effect = Exception("Not Saved")
        message_audit = {'msg_id': 'MsgId', 'msg_urn': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_audit(message_audit['msg_id'], message_audit['msg_urn'], mock_session)

    def test_saved_msg_event_has_been_saved(self):
        """retrieves message event from database"""
        message_event = {'msg_id': 'AMsgId', 'event': 'Draft_Saved', 'date_time': ''}
        with app.app_context():
            with current_app.test_request_context():
                Saver().save_message(SecureMessage(msg_id='AMsgId'))
                Saver().save_msg_event(message_event['msg_id'], message_event['event'])

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM events')
            for row in request:
                self.assertTrue(row is not None)
                self.assertTrue(row[1] == message_event['event'])
                self.assertTrue(row[2] == message_event['msg_id'])
                self.assertTrue(row[3] is not None)

    def test_save_event_raises_message_save_exception_on_db_error(self):
        """Tests MessageSaveException generated if db commit fails saving message event"""
        mock_session = mock.Mock(db.session)
        mock_session.commit.side_effect = Exception("Not Saved")

        message_event = {'msg_id': 'AMsgId', 'event': 'Draft_Saved', 'date_time': ''}
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_event(message_event['msg_id'], message_event['event'], mock_session)

    def test_status_commit_exception_raises_MessageSaveException(self):
        """check status commit exception clears the session"""
        message_status = {'msg_id': 'AMsgId', 'actor': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_status(message_status['actor'], message_status['msg_id'], 'INBOX, UNREAD')

    def test_event_commit_exception_raises_MessageSaveException(self):
        """check event commit exception clears the session"""
        message_event = {'msg_id': 'AMsgId', 'event': 'Draft_Saved', 'date_time': ''}
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_event(message_event['msg_id'], message_event['event'])

    def test_msg_commit_exception_does_a_rollback(self):
        """check message commit exception clears the session"""
        with app.app_context():
            self.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_message(self.test_message)

                self.db.create_all()
                Saver().save_message(self.test_message)

        with self.engine.connect() as con:
            request = con.execute('SELECT COUNT(secure_message.id) FROM secure_message')
            for row in request:
                self.assertTrue(row._row[0] == 1)

    def test_audit_commit_exception_raises_MessageSaveException(self):
        """check audit commit exception clears the session"""
        message_audit = {'msg_id': 'MsgId', 'msg_urn': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(MessageSaveException):
                    Saver().save_msg_audit(message_audit['msg_id'], message_audit['msg_urn'])
