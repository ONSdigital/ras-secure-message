import unittest
from flask import current_app
from flask import json
from sqlalchemy import create_engine
from app.application import app
from app.repository import database
from app.repository.retriever import Retriever
from tests.app.test_retriever import RetrieverTestCaseHelper
from app.common import utilities
from app.constants import MESSAGE_QUERY_LIMIT


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

    def test_paginated_to_json_returns_correct_messages_len(self):
        """turns paginated result list to json checking correct amount of messages are given"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(len(data['messages']), (MESSAGE_QUERY_LIMIT - 1))

    def test_paginated_to_json_returns_correct_message_self_link(self):
        """turns paginated result list to json checking correct self link has been added for message"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(data['messages'][4]['_links']['self']['href'],
                                 "{0}{1}".format(self.MESSAGE_BY_ID_ENDPOINT, data["messages"][4]['msg_id']))

    def test_paginated_to_json_returns_prev_page(self):
        """turns paginated result list to json checking prev page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT * 2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(2, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = utilities.paginated_list_to_json(resp, 2, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertTrue('prev' in data['_links'])

    def test_paginated_to_json_does_not_return_prev_page(self):
        """turns paginated result list to json checking prev page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertFalse('prev' in data['_links'])

    def test_paginated_to_json_returns_next_page(self):
        """turns paginated result list to json checking next page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT * 2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertTrue('next' in data['_links'])

    def test_paginated_to_json_does_not_return_next_page(self):
        """turns paginated result list to json checking next page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertFalse('next' in data['_links'])

    def test_paginated_to_json_has_correct_self_link(self):
        """turns paginated result list to json checking correct self link has been added for list"""
        self.populate_database(MESSAGE_QUERY_LIMIT - 1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = utilities.paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(data['_links']['self']['href'],
                                 "{0}?page={1}&limit={2}".format(self.MESSAGE_LIST_ENDPOINT, 1, MESSAGE_QUERY_LIMIT))

    def test_no_options(self):
        """Tests get messages list with no options provided"""
        args = {}

        string_query_args, page, limit, ru, survey, cc, label, business, desc = utilities.get_options(args)

        self.assertEqual(string_query_args, '?')
        self.assertEqual(page, 1)
        self.assertEqual(limit, MESSAGE_QUERY_LIMIT)
        self.assertEqual(ru, None)
        self.assertEqual(survey, None)
        self.assertEqual(cc, None)
        self.assertEqual(label, None)
        self.assertEqual(business, None)
        self.assertEqual(desc, True)

    def test_three_options(self):
        """Tests get messages list with few options provided"""
        args = {
            'page': 2,
            'survey': 'Survey',
            'ru': 'ReportingUnit'
        }
        string_query_args, page, limit, ru, survey, cc, label, business, desc = utilities.get_options(args)

        self.assertEqual(string_query_args, '?ru=ReportingUnit&survey=Survey')
        self.assertEqual(page, 2)
        self.assertEqual(limit, MESSAGE_QUERY_LIMIT)
        self.assertEqual(ru, 'ReportingUnit')
        self.assertEqual(survey, 'Survey')
        self.assertEqual(cc, None)
        self.assertEqual(label, None)
        self.assertEqual(business, None)
        self.assertEqual(desc, True)

    def test_all_options(self):
        """Tests get messages list with all options provided"""
        args = {
            'page': 2,
            'limit': 9,
            'survey': 'Survey',
            'ru': 'ReportingUnit',
            'cc': 'CollectionCase',
            'label': 'INBOX',
            'desc': 'false',
            'business': 'ABusiness',
        }
        string_query_args, page, limit, ru, survey, cc, label, business, desc = utilities.get_options(args)

        self.assertEqual(string_query_args,
                         '?ru=ReportingUnit&business=ABusiness&survey=Survey&cc=CollectionCase&label=INBOX&desc=false')
        self.assertEqual(page, 2)
        self.assertEqual(limit, 9)
        self.assertEqual(ru, 'ReportingUnit')
        self.assertEqual(survey, 'Survey')
        self.assertEqual(cc, 'CollectionCase')
        self.assertEqual(label, 'INBOX')
        self.assertEqual(desc, False)
        self.assertEqual(business, 'ABusiness')

    def test_add_string_query_no_args(self):
        """Adding args to empty string query"""
        string_query_args = '?'
        string_query_args = utilities.add_string_query_args(string_query_args, 'ru', 'ReportingUnit')
        self.assertEqual(string_query_args, '?ru=ReportingUnit')

    def test_add_string_query_with_args(self):
        """Adding args to string query with arg"""
        string_query_args = '?survey=Survey'
        string_query_args = utilities.add_string_query_args(string_query_args, 'ru', 'ReportingUnit')
        self.assertEqual(string_query_args, '?survey=Survey&ru=ReportingUnit')