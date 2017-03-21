import sys
sys.path.append('../ras-secure-message')
from app import application
import unittest
from flask import json
from sqlalchemy import create_engine
from app import settings
from app.repository.retriever import Retriever
from app.application import app
from flask import current_app
from app.data_model import database


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = settings.SECURE_MESSAGING_DATABASE_URL
        self.engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)
        with app.app_context():
            database.db.init_app(current_app)
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
        with self.engine.connect() as con:
            con.execute('DELETE FROM secure_message')
        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list()
                self.assertEqual(json.loads(response.get_data()), [])

    def test_all_msg_returned_when_db_less_than_15(self):
        with self.engine.connect() as con:
            con.execute('DELETE FROM secure_message')

        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list()
        self.assertEqual(len(json.loads(response.get_data())), 5)

    def test_15_msg_returned_when_db_greater_than_15(self):
        with self.engine.connect() as con:
            con.execute('DELETE FROM secure_message')

        self.populate_database(20)
        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list()
        self.assertEqual(len(json.loads(response.get_data())), 15)
