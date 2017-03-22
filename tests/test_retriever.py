import sys
sys.path.append('../ras-secure-message')
import unittest
from flask import json
from sqlalchemy import create_engine
from app.repository.retriever import Retriever
from app.application import app
from flask import current_app
from app.data_model import database


class RetrieverTestCase(unittest.TestCase):
    """Test case for message retrieval"""
    def setUp(self):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db', echo=True)
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db
        pass

    def populate_database(self, x=0):
        with self.engine.connect() as con:
            for i in range(x):
                query = 'INSERT INTO secure_message VALUES ({},"test", "test", "test")'.format(i)
                con.execute(query)
        pass

    def test_0_msg_returned_when_db_empty_true(self):
        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list()
                self.assertEqual(json.loads(response.get_data()), [])

    def test_all_msg_returned_when_db_less_than_15(self):
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list()
                self.assertEqual(len(json.loads(response.get_data())), 5)

    def test_15_msg_returned_when_db_greater_than_15(self):
        self.populate_database(20)
        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list()
                self.assertEqual(len(json.loads(response.get_data())), 15)

    def test_msg_returned_with_msg_id_true(self):
        id = 5
        self.populate_database(20)
        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message(id)
                msg = json.loads(response.get_data())
                self.assertEqual(msg['id'], id)
