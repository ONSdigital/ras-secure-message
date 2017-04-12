import unittest
from app.repository.saver import Saver
from sqlalchemy import create_engine
from app.repository import database
from flask import current_app, json
from app.application import app

from app.validation.domain import Message, MessageStatus


class SaverTestCase(unittest.TestCase):
    """Test case for message saving"""
    def setUp(self):
        """setup test environment"""
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db', echo=True)
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    def test_saved_message_has_saved_sent_date(self):
        """retrieves messages from database with less entries than retrieval amount"""
        message_object = Message(**{'subject': 'MyMessage',
                                    'body': 'hello', 'thread_id': ""})
        with app.app_context():
            with current_app.test_request_context():
                Saver().save_message(message_object)

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message')
            for row in request:
                data = {"sent_date": row['sent_date']}
                self.assertTrue(data['sent_date'] is not None)

    def test_saved_msg_status_has_been_saved(self):
        """retrieves message status from database"""
        messagestatus_object = {'msg_id': 'AMsgId', 'actor': 'Tej'}
        with app.app_context():
            with current_app.test_request_context():
                Saver().save_msg_status(messagestatus_object['msg_id'], messagestatus_object['actor'], 'INBOX, UNREAD')

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM status')
            for row in request:
                self.assertTrue(row is not None)
