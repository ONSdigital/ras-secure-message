import unittest
from flask import json
from sqlalchemy import create_engine
from app.repository.retriever import Retriever
from app.application import app
from flask import current_app
from app.data_model import database
from werkzeug.exceptions import NotFound
from app.settings import MESSAGE_QUERY_LIMIT


class RetrieverTestCase(unittest.TestCase):
    """Test case for message retrieval"""
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

    def populate_database(self, x=0):
        with self.engine.connect() as con:
            for i in range(x):
                query = 'INSERT INTO secure_message VALUES ({}, "AMsg_Id", "test", "test", "test","test","",0,0,\
                "2017-02-03 00:00:00", "2017-02-03 00:00:00")'.format(i)
                con.execute(query)

    def test_0_msg_returned_when_db_empty_true(self):
        """retrieves messages from empty database"""
        with app.app_context():
            with current_app.test_request_context():
                status, response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)
                msg = []
                for message in response.items:
                    msg.append(message.serialize)
                self.assertEqual(msg, [])

    def test_all_msg_returned_when_db_less_than_limit(self):
        """retrieves messages from database with less entries than retrieval amount"""
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                status, response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)
                msg = []
                for message in response.items:
                    msg.append(message.serialize)
                self.assertEqual(len(msg), 5)

    def test_15_msg_returned_when_db_greater_than_limit(self):
        """retrieves x messages when database has greater than x entries"""
        self.populate_database(MESSAGE_QUERY_LIMIT+5)
        with app.app_context():
            with current_app.test_request_context():
                status, response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)
                msg = []
                for message in response.items:
                    msg.append(message.serialize)
                self.assertEqual(len(msg), MESSAGE_QUERY_LIMIT)

    def test_msg_returned_with_msg_id_true(self):
        """retrieves message using id"""
        message_id = 5
        self.populate_database(20)
        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message(message_id)
                msg = json.loads(response.get_data())
                self.assertEqual(msg['id'], message_id)

    def test_msg_returned_with_msg_id_returns_404(self):
        """retrieves message using id that doesn't exist"""
        message_id = 1
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id)

    def test_msg_returned_with_msg_id_msg_not_in_database(self):
        """retrieves message using id"""
        message_id = 21
        self.populate_database(20)
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id)
