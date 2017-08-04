import hashlib
import unittest
from flask import current_app, json
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from app.application import app
from app.common import utilities
from app.common.utilities import generate_etag
from app.repository import database
from app.repository.retriever import Retriever
from app.constants import MESSAGE_QUERY_LIMIT
from app.validation.user import User
from tests.app.test_retriever import RetrieverTestCaseHelper
from app.services.service_toggles import party


class RetrieverTestCase(unittest.TestCase, RetrieverTestCaseHelper):
    """Test case for message retrieval"""
    def setUp(self):
        """setup test environment"""
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')
        self.MESSAGE_LIST_ENDPOINT = "http://localhost:5050/messages"
        self.MESSAGE_BY_ID_ENDPOINT = "http://localhost:5050/message/"
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db
        party.use_mock_service()

        self.user = User('0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'respondent')

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """enable foreign key constraint for tests"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def test_paginated_to_json_returns_correct_messages_len(self):
        """turns paginated result list to json checking correct amount of messages are given"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, self.user)[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT, "http://localhost:5050/", self.user, string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(len(data['messages']), (MESSAGE_QUERY_LIMIT - 1))

    def test_paginated_to_json_returns_correct_message_self_link(self):
        """turns paginated result list to json checking correct self link has been added for message"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, self.user)[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT, "http://localhost:5050/", self.user, string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(data['messages'][4]['_links']['self']['href'],
                                 "{0}{1}".format(self.MESSAGE_BY_ID_ENDPOINT, data["messages"][4]['msg_id']))

    def test_paginated_to_json_returns_prev_page(self):
        """turns paginated result list to json checking prev page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT * 2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(2, MESSAGE_QUERY_LIMIT, self.user)[1]
                json_data = utilities.paginated_list_to_json(resp, 2, MESSAGE_QUERY_LIMIT, "http://localhost:5050/", self.user, string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertTrue('prev' in data['_links'])

    def test_paginated_to_json_does_not_return_prev_page(self):
        """turns paginated result list to json checking prev page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, self.user)[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT, "http://localhost:5050/", self.user, string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertFalse('prev' in data['_links'])

    def test_paginated_to_json_returns_next_page(self):
        """turns paginated result list to json checking next page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT * 2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, self.user)[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT, "http://localhost:5050/", self.user, string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertTrue('next' in data['_links'])

    def test_paginated_to_json_does_not_return_next_page(self):
        """turns paginated result list to json checking next page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, self.user)[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT, "http://localhost:5050/", self.user, string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertFalse('next' in data['_links'])

    def test_paginated_to_json_has_correct_self_link(self):
        """turns paginated result list to json checking correct self link has been added for list"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, self.user)[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT, "http://localhost:5050/", self.user, string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(data['_links']['self']['href'],
                                 "{0}?page={1}&limit={2}".format(self.MESSAGE_LIST_ENDPOINT, 1, MESSAGE_QUERY_LIMIT))

    def test_no_options(self):
        """Tests get messages list with no options provided"""
        args = {}

        string_query_args, page, limit, ru_id, survey, cc, label, desc, ce = utilities.get_options(args)

        self.assertEqual(string_query_args, '?')
        self.assertEqual(page, 1)
        self.assertEqual(limit, MESSAGE_QUERY_LIMIT)
        self.assertEqual(ru_id, None)
        self.assertEqual(survey, None)
        self.assertEqual(cc, None)
        self.assertEqual(label, None)
        self.assertEqual(desc, True)
        self.assertEqual(ce, None)

    def test_three_options(self):
        """Tests get messages list with few options provided"""
        args = {
            'page': 2,
            'survey': 'BRES',
            'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b'
        }

        string_query_args, page, limit, ru_id, survey, cc, label, desc, ce = utilities.get_options(args)

        self.assertEqual(string_query_args, '?ru_id=7fc0e8ab-189c-4794-b8f4-9f05a1db185b&survey=BRES')
        self.assertEqual(page, 2)
        self.assertEqual(limit, MESSAGE_QUERY_LIMIT)
        self.assertEqual(ru_id, '7fc0e8ab-189c-4794-b8f4-9f05a1db185b')
        self.assertEqual(survey, 'BRES')
        self.assertEqual(cc, None)
        self.assertEqual(label, None)
        self.assertEqual(desc, True)
        self.assertEqual(ce, None)

    def test_all_options(self):
        """Tests get messages list with all options provided"""
        args = {
            'page': 2,
            'limit': 9,
            'survey': 'BRES',
            'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
            'cc': 'CollectionCase',
            'label': 'INBOX',
            'desc': 'false',
            'ce': 'CollectionExercise'
        }
        string_query_args, page, limit, ru_id, survey, cc, label, desc, ce = utilities.get_options(args)

        self.assertEqual(string_query_args,
                         '?ru_id=7fc0e8ab-189c-4794-b8f4-9f05a1db185b&survey=BRES&cc=CollectionCase&label=INBOX&ce=CollectionExercise&desc=false')

        self.assertEqual(page, 2)
        self.assertEqual(limit, 9)
        self.assertEqual(ru_id, '7fc0e8ab-189c-4794-b8f4-9f05a1db185b')
        self.assertEqual(survey, 'BRES')
        self.assertEqual(cc, 'CollectionCase')
        self.assertEqual(label, 'INBOX')
        self.assertEqual(desc, False)
        self.assertEqual(ce, 'CollectionExercise')

    def test_add_string_query_no_args(self):
        """Adding args to empty string query"""
        string_query_args = '?'
        string_query_args = utilities.add_string_query_args(string_query_args, 'ru_id', '7fc0e8ab-189c-4794-b8f4-9f05a1db185b')
        self.assertEqual(string_query_args, '?ru_id=7fc0e8ab-189c-4794-b8f4-9f05a1db185b')

    def test_add_string_query_with_args(self):
        """Adding args to string query with arg"""
        string_query_args = '?survey=BRES'
        string_query_args = utilities.add_string_query_args(string_query_args, 'ru_id', '7fc0e8ab-189c-4794-b8f4-9f05a1db185b')
        self.assertEqual(string_query_args, '?survey=BRES&ru_id=7fc0e8ab-189c-4794-b8f4-9f05a1db185b')

    def test_generate_etag_with_none_in_msg_to(self):
        """Generating etag when msg_to has a None value"""

        generated_etag = generate_etag([], 'd740-10d5-4ecb-b', 'subject', 'body')

        msg_to = []
        msg_to_str = ' '.join(str(uuid) for uuid in msg_to)

        data_to_hash = {
            'msg_to': msg_to_str,
            'msg_id': 'd740-10d5-4ecb-b',
            'subject': 'subject',
            'body': 'body'
        }

        hash_object = hashlib.sha1(str(sorted(data_to_hash.items())).encode())
        etag = hash_object.hexdigest()

        self.assertEqual(generated_etag, etag)

    def test_generate_etag_with_msg_to(self):
        """Generating etag when msg_to has a uuid value"""

        generated_etag = generate_etag(['7fc0e8ab-189c-4794-b8f4-9f05a1db185b'], 'd740-10d5-4ecb-b', 'subject', 'body')

        msg_to = ['7fc0e8ab-189c-4794-b8f4-9f05a1db185b']
        msg_to_str = ' '.join(str(uuid) for uuid in msg_to)

        data_to_hash = {
            'msg_to': msg_to_str,
            'msg_id': 'd740-10d5-4ecb-b',
            'subject': 'subject',
            'body': 'body'
        }

        hash_object = hashlib.sha1(str(sorted(data_to_hash.items())).encode())
        etag = hash_object.hexdigest()

        self.assertEqual(generated_etag, etag)

    def test_generate_etag_with_multiple_msg_to(self):
        """Generating etag when msg_to has a uuid value"""

        generated_etag = generate_etag(['1', '2', '3'], 'd740-10d5-4ecb-b', 'subject', 'body')

        msg_to = ['1', '2', '3']
        msg_to_str = ' '.join(str(uuid) for uuid in msg_to)

        data_to_hash = {
            'msg_to': msg_to_str,
            'msg_id': 'd740-10d5-4ecb-b',
            'subject': 'subject',
            'body': 'body'
        }

        hash_object = hashlib.sha1(str(sorted(data_to_hash.items())).encode())
        etag = hash_object.hexdigest()

        self.assertEqual(generated_etag, etag)
