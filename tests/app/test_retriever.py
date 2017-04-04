import unittest
from flask import json
from sqlalchemy import create_engine
from app.repository.retriever import Retriever
from app.application import app
from flask import current_app
from app.data_model import database
from werkzeug.exceptions import NotFound, InternalServerError
from app.settings import MESSAGE_QUERY_LIMIT
from app.resources.messages import MessageList
import uuid


class RetrieverTestCase(unittest.TestCase):
    """Test case for message retrieval"""
    def setUp(self):
        """setup test environment"""
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db', echo=True)
        self.MESSAGE_LIST_ENDPOINT = "http://localhost:5050/messages"
        self.MESSAGE_BY_ID_ENDPOINT = "http://localhost:5050/message/"
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    def populate_database(self, x=0):
        with self.engine.connect() as con:
            for i in range(x):
                msg_id = str(uuid.uuid4())
                query = 'INSERT INTO secure_message VALUES ({0}, "{1}", "test", "test", "test","test","",0,0,\
                "2017-02-03 00:00:00", "2017-02-03 00:00:00", "ACollectionCase",\
                "AReportingUnit", "ACollectionInstrument")'.format(i,msg_id)
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

    def test_retrieve_message_list_raises_error(self):
        """retrieves messages from when db does not exist"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)

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

    def test_retrieve_message_raises_error(self):
        """retrieves message from when db does not exist"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().retrieve_message(1)

    def test_paginated_to_json_returns_correct_messages_len(self):
        """turns paginated result list to json checking correct amount of messages are given"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/")
                data = json.loads(json_data.get_data())
                self.assertEqual(len(data['messages']), (MESSAGE_QUERY_LIMIT-1))

    def test_paginated_to_json_returns_correct_message_self_link(self):
        """turns paginated result list to json checking correct self link has been added for message"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/")
                data = json.loads(json_data.get_data())
                self.assertEqual(data['messages']['4']['_links']['self']['href'],
                                 "{0}{1}".format(self.MESSAGE_BY_ID_ENDPOINT, data["messages"]['4']['id']))

    def test_paginated_to_json_returns_prev_page(self):
        """turns paginated result list to json checking prev page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT*2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(2, MESSAGE_QUERY_LIMIT)[1]
                json_data = MessageList()._paginated_list_to_json(resp, 2, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/")
                data = json.loads(json_data.get_data())
                self.assertTrue('prev' in data['_links'])

    def test_paginated_to_json_does_not_return_prev_page(self):
        """turns paginated result list to json checking prev page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/")
                data = json.loads(json_data.get_data())
                self.assertFalse('prev' in data['_links'])

    def test_paginated_to_json_returns_next_page(self):
        """turns paginated result list to json checking next page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT*2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/")
                data = json.loads(json_data.get_data())
                self.assertTrue('next' in data['_links'])

    def test_paginated_to_json_does_not_return_next_page(self):
        """turns paginated result list to json checking next page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/")
                data = json.loads(json_data.get_data())
                self.assertFalse('next' in data['_links'])

    def test_paginated_to_json_has_correct_self_link(self):
        """turns paginated result list to json checking correct self link has been added for list"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT)[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/")
                data = json.loads(json_data.get_data())
                self.assertEqual(data['_links']['self']['href'],
                                 "{0}?page={1}&limit={2}".format(self.MESSAGE_LIST_ENDPOINT, 1, MESSAGE_QUERY_LIMIT))
