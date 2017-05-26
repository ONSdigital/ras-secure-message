import unittest
import uuid
from flask import current_app
from flask import json
from sqlalchemy import create_engine
from werkzeug.exceptions import NotFound, InternalServerError
from app.application import app
from app.repository import database
from app.repository.retriever import Retriever
from app.resources.messages import MessageList
from app.settings import MESSAGE_QUERY_LIMIT
from datetime import datetime
import random


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
            database.db.engine.execute('pragma foreign_keys=ON')
            self.db = database.db

    def populate_database(self, no_of_messages=0, single=True, add_reply=False, add_draft=False, multiple_users=False):
        with self.engine.connect() as con:
            for _ in range(no_of_messages):
                year = 2016
                month = random.choice(range(1, 13))
                day = random.choice(range(1, 25))
                sent_date = datetime(year, month, day)
                if single:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                            ' collection_case, reporting_unit, survey) VALUES ("{0}", "test","test","", ' \
                            '"ACollectionCase", "AReportingUnit", ' \
                            '"SurveyType")'.format(msg_id)
                    res = con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("SENT", "{0}", "respondent.21345")'.format(
                        msg_id)
                    res = con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("INBOX", "{0}", "SurveyType")'.format(
                        msg_id)
                    res = con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("UNREAD", "{0}", "SurveyType")'.format(
                        msg_id)
                    res = con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Sent", "{0}", "{1}")'.format(
                        msg_id, sent_date)
                    res = con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Read", "{0}", "{1}")'.format(
                        msg_id, str(datetime(year, month, day+1)))
                    res = con.execute(query)
                if add_reply:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id, ' \
                            ' collection_case, reporting_unit, survey) VALUES ("{0}", "test","test","", ' \
                            ' "ACollectionCase", "AReportingUnit", ' \
                            '"SurveyType")'.format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("SENT", "{0}", "SurveyType")'.format(
                        msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("INBOX", "{0}", "respondent.21345")'\
                        .format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("UNREAD", "{0}", "respondent.21345")'\
                        .format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Sent", "{0}", "{1}")'.format(
                        msg_id, sent_date)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Read", "{0}", "{1}")'.format(
                        msg_id, "2017-02-03 00:00:00")
                    con.execute(query)
                if add_draft:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id, ' \
                            ' collection_case, reporting_unit, survey) VALUES ("{0}", "test","test","", ' \
                            ' "ACollectionCase", "AReportingUnit", ' \
                            '"SurveyType")'.format(msg_id)
                    res = con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT_INBOX", "{0}", "respondent.21345")'.format(
                        msg_id)
                    res = con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT", "{0}",' \
                            ' "SurveyType")'.format(msg_id)
                    res = con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Draft_Saved", "{0}", "{1}")'.format(
                        msg_id, datetime(year, random.choice(range(1, 13)), day))
                    res = con.execute(query)
                if multiple_users:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id, ' \
                            ' collection_case, reporting_unit, survey) VALUES ("{0}", "test","test","", ' \
                            ' "AnotherCollectionCase", ' \
                            '"AnotherReportingUnit", "AnotherSurveyType")'.format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("SENT", "{0}", "respondent.0000")'\
                        .format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("INBOX", "{0}", "AnotherSurveyType")'\
                        .format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("UNREAD", "{0}", "AnotherSurveyType")'\
                        .format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Sent", "{0}", "{1}")'.format(
                        msg_id, sent_date)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Read", "{0}", "{1}")'.format(
                        msg_id, "2017-02-03 00:00:00")
                    con.execute(query)

    def test_0_msg_returned_when_db_empty_true(self):
        """retrieves messages from empty database"""
        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
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
                    Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')

    def test_all_msg_returned_when_db_less_than_limit(self):
        """retrieves messages from database with less entries than retrieval amount"""
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                msg = []
                for message in response.items:
                    msg.append(message.serialize)
                self.assertEqual(len(msg), 5)

    def test_msg_limit_returned_when_db_greater_than_limit(self):
        """retrieves x messages when database has greater than x entries"""
        self.populate_database(MESSAGE_QUERY_LIMIT+5)
        with app.app_context():
            with current_app.test_request_context():
                result = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                msg = []
                for message in result.items:
                    msg.append(message.serialize)
                self.assertEqual(len(msg), MESSAGE_QUERY_LIMIT)

    def test_msg_returned_with_msg_id_true(self):
        """retrieves message using id"""
        # message_id = ""
        self.populate_database(20)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'internal.21345')
                    self.assertEqual(response['msg_id'], str(names[0]))

    def test_msg_returned_with_msg_id_returns_404(self):
        """retrieves message using id that doesn't exist"""
        message_id = 1
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id, 'internal.21345')

    def test_msg_returned_with_msg_id_msg_not_in_database(self):
        """retrieves message using id"""
        message_id = 21
        self.populate_database(20)
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id, 'internal.21345')

    def test_correct_labels_returned_internal(self):
        """retrieves message using id and checks the labels are correct"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'internal.21345')
                    labels = ['INBOX', 'UNREAD']
                    self.assertCountEqual(response['labels'], labels)

    def test_correct_labels_returned_external(self):
        """retrieves message using id and checks the labels are correct"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'respondent.21345')
                    labels = ['SENT']
                    self.assertCountEqual(response['labels'], labels)

    def test_correct_to_and_from_returned(self):
        """retrieves message using id and checks the to and from urns are correct"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'respondent.21345')
                    urn_to = ['SurveyType']
                    self.assertEqual(response['urn_to'], urn_to)
                    self.assertEqual(response['urn_from'], 'respondent.21345')

    def test_retrieve_message_raises_error(self):
        """retrieves message from when db does not exist"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().retrieve_message(1, 'internal.21345')

    def test_paginated_to_json_returns_correct_messages_len(self):
        """turns paginated result list to json checking correct amount of messages are given"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(len(data['messages']), (MESSAGE_QUERY_LIMIT-1))

    def test_paginated_to_json_returns_correct_message_self_link(self):
        """turns paginated result list to json checking correct self link has been added for message"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(data['messages']['4']['_links']['self']['href'],
                                 "{0}{1}".format(self.MESSAGE_BY_ID_ENDPOINT, data["messages"]['4']['msg_id']))

    def test_paginated_to_json_returns_prev_page(self):
        """turns paginated result list to json checking prev page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT*2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(2, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = MessageList()._paginated_list_to_json(resp, 2, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertTrue('prev' in data['_links'])

    def test_paginated_to_json_does_not_return_prev_page(self):
        """turns paginated result list to json checking prev page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertFalse('prev' in data['_links'])

    def test_paginated_to_json_returns_next_page(self):
        """turns paginated result list to json checking next page is returned if needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT*2)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertTrue('next' in data['_links'])

    def test_paginated_to_json_does_not_return_next_page(self):
        """turns paginated result list to json checking next page is not returned if not needed"""
        self.populate_database(MESSAGE_QUERY_LIMIT-1)
        with app.app_context():
            with current_app.test_request_context():
                resp = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
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
                json_data = MessageList()._paginated_list_to_json(resp, 1, MESSAGE_QUERY_LIMIT,
                                                                  "http://localhost:5050/", 'respondent.21345',
                                                                  string_query_args='?')
                data = json.loads(json_data.get_data())
                self.assertEqual(data['_links']['self']['href'],
                                 "{0}?page={1}&limit={2}".format(self.MESSAGE_LIST_ENDPOINT, 1, MESSAGE_QUERY_LIMIT))

    def test_all_draft_message_returned(self):
        """retrieves messages from database with label DRAFT for user"""
        self.populate_database(5, add_draft=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT,
                                                             'internal.21345', survey='SurveyType', label='DRAFT')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('internal.21345')
                    msg.append(serialized_msg)
                    self.assertTrue('DRAFT' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_sent_message_returned(self):
        """retrieves messages from database with label SENT for user"""
        self.populate_database(5, add_reply=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             label="SENT")[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue('SENT' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_inbox_message_returned(self):
        """retrieves messages from database with label SENT for user"""
        self.populate_database(5, add_reply=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'internal.21345',
                                                             label="INBOX", survey='SurveyType')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('internal.21345')
                    msg.append(serialized_msg)
                    self.assertTrue('INBOX' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_message_returned_no_label_option(self):
        """retrieves all messages from database for user with no messages with label DRAFT_INBOX"""
        self.populate_database(5, add_draft=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]

                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertFalse('DRAFT_INBOX' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_message_returned_with_ru_option(self):
        """retrieves all messages from database for user with ru option"""
        self.populate_database(5, multiple_users=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             ru='AReportingUnit')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['reporting_unit'] == 'AReportingUnit')
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_ru_option(self):
        """retrieves no messages from database for user with ru option"""
        self.populate_database(5, multiple_users=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             ru='AnotherReportingUnit')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['reporting_unit'] == 'AnotherReportingUnit')
                self.assertEqual(len(msg), 0)

    def test_all_message_returned_with_survey_option(self):
        """retrieves all messages from database for user with survey option"""
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             survey='SurveyType')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['survey'] == 'SurveyType')
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_survey_option(self):
        """retrieves no messages from database for user with survey option"""
        self.populate_database(5, multiple_users=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             survey='AnotherSurveyType')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['survey'] == 'AnotherSurveyType')
                self.assertEqual(len(msg), 0)

    def test_all_message_returned_with_cc_option(self):
        """retrieves all messages from database for user with cc option"""
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             cc='ACollectionCase')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['collection_case'] == 'ACollectionCase')
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_cc_option(self):
        """retrieves no messages from database for user with cc option"""
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             cc='AnotherCollectionCase')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['collection_case'] == 'AnotherCollectionCase')
                self.assertEqual(len(msg), 0)

    def test_message_list_returned_in_descending_order(self):
        """retrieves messages from database in desc sent_date order"""
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             descend=True)[1]
                sent = []
                read = []
                modified = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    sent.append(serialized_msg['sent_date'])
                    read.append(serialized_msg['read_date'])
                    modified.append(serialized_msg['modified_date'])

                desc_date = sorted(sent, reverse=True)
                self.assertEqual(len(sent), 5)
                self.assertListEqual(desc_date, sent)

    def test_message_list_returned_in_ascending_order(self):
        """retrieves messages from database in asc sent_date order"""
        self.populate_database(5)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             descend=False)[1]
                sent = []
                read = []
                modified = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    sent.append(serialized_msg['sent_date'])
                    read.append(serialized_msg['read_date'])
                    modified.append(serialized_msg['modified_date'])

                asc_date = sorted(sent, reverse=False)
                self.assertEqual(len(sent), 5)
                self.assertListEqual(asc_date, sent)

    def test_message_and_draft_list_returned_in_ascending_order(self):
        """retrieves messages and drafts from database in asc sent_date order"""
        self.populate_database(5, add_draft=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'internal.21345',
                                                             survey='SurveyType',
                                                             descend=False)[1]
                sent = []
                read = []
                modified = []
                date = []
                for message in response.items:
                    serialized_msg = message.serialize('internal.21345')
                    sent.append(serialized_msg['sent_date'])
                    read.append(serialized_msg['read_date'])
                    modified.append(serialized_msg['modified_date'])

                for x in range(0, len(sent)):
                    if sent[x] != 'N/A':
                        date.append(sent[x])
                    else:
                        date.append(modified[x])

                asc_date = sorted(date, reverse=False)
                self.assertEqual(len(date), 10)
                self.assertListEqual(asc_date, date)

    def test_message_and_draft_list_returned_in_descending_order(self):
        """retrieves messages and drafts from database in desc sent_date order"""
        self.populate_database(5, add_draft=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'internal.21345',
                                                             survey='SurveyType',
                                                             descend=True)[1]
                sent = []
                read = []
                modified = []
                date = []
                for message in response.items:
                    serialized_msg = message.serialize('internal.21345')
                    sent.append(serialized_msg['sent_date'])
                    read.append(serialized_msg['read_date'])
                    modified.append(serialized_msg['modified_date'])

                for x in range(0, len(sent)):
                    if sent[x] != 'N/A':
                        date.append(sent[x])
                    else:
                        date.append(modified[x])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 10)
                self.assertListEqual(desc_date, date)

    def test_no_options(self):
        """Tests get messages list with no options provided"""
        args = {}

        string_query_args, page, limit, ru, survey, cc, label, desc = MessageList._get_options(args)

        self.assertEqual(string_query_args, '?')
        self.assertEqual(page, 1)
        self.assertEqual(limit, MESSAGE_QUERY_LIMIT)
        self.assertEqual(ru, None)
        self.assertEqual(survey, None)
        self.assertEqual(cc, None)
        self.assertEqual(label, None)
        self.assertEqual(desc, True)

    def test_three_options(self):
        """Tests get messages list with few options provided"""
        args = {
            'page': 2,
            'survey': 'Survey',
            'ru': 'ReportingUnit'
        }
        string_query_args, page, limit, ru, survey, cc, label, desc = MessageList._get_options(args)

        self.assertEqual(string_query_args, '?ru=ReportingUnit&survey=Survey')
        self.assertEqual(page, 2)
        self.assertEqual(limit, MESSAGE_QUERY_LIMIT)
        self.assertEqual(ru, 'ReportingUnit')
        self.assertEqual(survey, 'Survey')
        self.assertEqual(cc, None)
        self.assertEqual(label, None)
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
            'desc': 'false'

        }
        string_query_args, page, limit, ru, survey, cc, label, desc = MessageList._get_options(args)

        self.assertEqual(string_query_args, '?ru=ReportingUnit&survey=Survey&cc=CollectionCase&label=INBOX&desc=false')
        self.assertEqual(page, 2)
        self.assertEqual(limit, 9)
        self.assertEqual(ru, 'ReportingUnit')
        self.assertEqual(survey, 'Survey')
        self.assertEqual(cc, 'CollectionCase')
        self.assertEqual(label, 'INBOX')
        self.assertEqual(desc, False)

    def test_add_string_query_no_args(self):
        string_query_args = '?'
        string_query_args = MessageList._add_string_query_args(string_query_args, 'ru', 'ReportingUnit')
        self.assertEqual(string_query_args, '?ru=ReportingUnit')

    def test_add_string_query_with_args(self):
        string_query_args = '?survey=Survey'
        string_query_args = MessageList._add_string_query_args(string_query_args, 'ru', 'ReportingUnit')
        self.assertEqual(string_query_args, '?survey=Survey&ru=ReportingUnit')

    def test_draft_returned_with_msg_id_true(self):
        """retrieves draft using id"""

        self.populate_database(1, single=False, add_draft=True)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_draft(msg_id, 'internal.21345')
                    self.assertEqual(response['msg_id'], str(names[0]))

    def test_modified_date_returned_for_draft(self):
        """retrieves draft using id and checks the modified dates returned"""
        self.populate_database(1, single=False, add_draft=True)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_draft(msg_id, 'internal.21345')
                    self.assertTrue(response['modified_date'] != "N/A")
                    self.assertEqual(response['read_date'], 'N/A')
                    self.assertEqual(response['sent_date'], "N/A")

    def test_sent_date_returned_for_message(self):
        """retrieves message using id and checks the sent date returned"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'internal.21345')
                    self.assertEqual(response['modified_date'], "N/A")
                    self.assertTrue(response['sent_date'] != "N/A")

    def test_read_date_returned_for_message(self):
        """retrieves message using id and checks the read date returned"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'internal.21345')
                    self.assertEqual(response['modified_date'], "N/A")
                    self.assertTrue(response['read_date'] != "N/A")

    def test_retrieve_draft_with_a_message_msg_id_returns_404(self):
        """retrieves draft using id of an existing message"""
        self.populate_database(1, single=True)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with app.app_context():
                with current_app.test_request_context():
                    message_id = str(names[0])
                    with self.assertRaises(NotFound):
                        Retriever().retrieve_draft(message_id, 'internal.21345')

    def test_draft_returned_with_msg_id_draft_not_in_database(self):
        """retrieves draft using id where draft not in database"""
        message_id = str(uuid.uuid4())
        self.populate_database(1, single=False, add_draft=True)
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id, 'internal.21345')

    def test_correct_labels_returned_for_draft(self):
        """retrieves draft using id and checks the labels are correct"""
        self.populate_database(1, single=False, add_draft=True)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'internal.21345')
                    labels = ['DRAFT']
                    self.assertCountEqual(response['labels'], labels)

    def test_correct_to_and_from_returned_for_draft(self):
        """retrieves draft using id and checks the to and from urns are correct"""
        self.populate_database(1, single=False, add_draft=True)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, 'internal.21345')
                    self.assertEqual(response['urn_to'], ['respondent.21345'])
                    self.assertEqual(response['urn_from'], 'SurveyType')

    def test_retrieve_draft_raises_error(self):
        """retrieves draft from when db does not exist"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().retrieve_message(1, 'internal.21345')
