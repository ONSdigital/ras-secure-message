import unittest
from app.repository.saver import Saver
from sqlalchemy import create_engine
from app.repository import database
from app.repository.database import db
from flask import current_app
from app.application import app
from unittest import mock
from app.exception.exceptions import MessageSaveException
from app.validation.domain import Message
from datetime import datetime, timezone


class SaverTestCase(unittest.TestCase):
    """Test case for message saving"""
    def setUp(self):
        """setup test environment"""
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db', echo=True)
        self.test_message = Message(**{'urn_to': 'tej', 'urn_from': 'gemma', 'subject': 'MyMessage',
                                    'body': 'hello', 'thread_id': ""})
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    # def test_saved_message_has_saved_sent_date(self):
    #
    #     message = Message(**{'msg_id': 'Amsgid','urn_to': 'tej', 'urn_from': 'gemma', 'subject': 'MyMessage',
    #                       'body': 'hello', 'thread_id': ""})
    #
    #     with app.app_context():
    #         with current_app.test_request_context():
    #             Saver().save_message(message)
    #
    #         with self.engine.connect() as con:
    #             request = con.execute("SELECT * FROM secure_message WHERE msg_id='Amsgid'")
    #             for row in request:
    #                 data = {"sent_date": row['sent_date']}
    #                 self.assertTrue(data['sent_date'] is not None)

    # def test_saved_message_has_not_saved_sent_date(self):
    #
    #     message = Message(**{'msg_id': 'Amsgid','urn_to': 'tej', 'urn_from': 'gemma', 'subject': 'MyMessage',
    #                       'body': 'hello', 'thread_id': ""})
    #
    #     with app.app_context():
    #         with current_app.test_request_context():
    #             Saver().save_message(message)
    #
    #         with self.engine.connect() as con:
    #             request = con.execute("SELECT * FROM secure_message WHERE msg_id='Amsgid'")
    #             for row in request:
    #                 data = {"sent_date": row['sent_date']}
    #                 self.assertTrue(data['sent_date'] is None)

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
                Saver().save_msg_status(message_status['msg_id'], message_status['actor'], 'INBOX, UNREAD')

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
                    Saver().save_msg_status(message_status['msg_id'], message_status['actor'], 'INBOX', mock_session)

    def test_msg_audit_has_been_saved(self):
        """Tests message audit is saved to database"""
        message_audit = {'msg_id': 'MsgId', 'msg_urn': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                Saver().save_msg_audit(message_audit['msg_id'], message_audit['msg_urn'])

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM internal_sent_audit')
            for row in request:
                self.assertTrue(row is not None)

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
                Saver().save_msg_event(message_event['msg_id'], message_event['event'])

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM events')
            for row in request:
                self.assertTrue(row is not None)
                self.assertTrue(row[1] == message_event['event'])
                self.assertTrue(row[2] == message_event['msg_id'])
                self.assertTrue(row[3] is not None)
