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
from app.constants import MESSAGE_QUERY_LIMIT
from datetime import datetime
import random


class RetrieverTestCaseHelper:
    """Helper class for Retriever Tests"""

    def populate_database(self, no_of_messages=0, single=True, add_reply=False, add_draft=False, multiple_users=False):
        """ Populate the db with a specified number of messages and optionally replies , multiple users"""
        with self.engine.connect() as con:
            for _ in range(no_of_messages):
                year = 2016
                month = random.choice(range(1, 13))
                draft_month = random.choice(range(1, 13))
                day = random.choice(range(1, 25))
                sent_date = datetime(year, month, day)
                if single:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                            ' collection_case, reporting_unit, survey, business_name) VALUES ("{0}", "test","test",' \
                            '"ThreadId", "ACollectionCase", "AReportingUnit", "SurveyType", "ABusiness")'.format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("SENT", "{0}", "respondent.21345")'.format(
                        msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("INBOX", "{0}", "SurveyType")'.format(
                        msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("UNREAD", "{0}", "SurveyType")'.format(
                        msg_id)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Sent", "{0}", "{1}")'.format(
                        msg_id, sent_date)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Read", "{0}", "{1}")'.format(
                        msg_id, str(datetime(year, month, day+1)))
                    con.execute(query)
                if add_reply:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                            ' collection_case, reporting_unit, survey, business_name) VALUES ("{0}", "test","test",' \
                            '"ThreadId", "ACollectionCase", "AReportingUnit", "SurveyType", "ABusiness")'.format(msg_id)
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
                        msg_id, str(datetime(year, month, day+2)))
                    con.execute(query)
                if add_draft:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                            ' collection_case, reporting_unit, survey, business_name) VALUES ("{0}", "test","test",' \
                            '"ThreadId", "ACollectionCase", "AReportingUnit", "SurveyType", "ABusiness")'.format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT_INBOX", "{0}", "respondent.21345")'.format(
                        msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT", "{0}",' \
                            ' "SurveyType")'.format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Draft_Saved", "{0}", "{1}")'.format(
                        msg_id, datetime(year, draft_month, day))
                    con.execute(query)
                if multiple_users:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                            ' collection_case, reporting_unit, survey, business_name) VALUES ("{0}", "test","test",' \
                            '"", "AnotherCollectionCase", "AnotherReportingUnit", "AnotherSurveyType", ' \
                            '"AnotherBusiness")'.format(msg_id)
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

    def create_threads(self, no_of_threads=1):
        """ Populate the db with a specified number of messages and optionally replies , multiple users"""
        threads = []
        with self.engine.connect() as con:
            for _ in range(no_of_threads):
                year = 2016
                month = random.choice(range(1, 13))
                day = random.choice(range(1, 22))
                sent_date = datetime(year, month, day)

                msg_id = str(uuid.uuid4())
                thread_id = msg_id
                threads.append(thread_id)
                query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                        ' collection_case, reporting_unit, survey, business_name) VALUES ("{0}", "test","test",' \
                        '"{1}", "ACollectionCase", "AReportingUnit", "BRES", "ABusiness")'.format(
                    msg_id, thread_id)
                con.execute(query)
                query = 'INSERT INTO status(label, msg_id, actor) VALUES("SENT", "{0}", "respondent.21345")'.format(
                    msg_id)
                con.execute(query)
                query = 'INSERT INTO status(label, msg_id, actor) VALUES("INBOX", "{0}", "BRES")'.format(
                    msg_id)
                con.execute(query)
                query = 'INSERT INTO status(label, msg_id, actor) VALUES("UNREAD", "{0}", "BRES")'.format(
                    msg_id)
                con.execute(query)
                query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Sent", "{0}", "{1}")'.format(
                    msg_id, sent_date)
                con.execute(query)
                query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Read", "{0}", "{1}")'.format(
                    msg_id, str(datetime(year, month, day + 1)))
                con.execute(query)

                msg_id = str(uuid.uuid4())
                query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                        ' collection_case, reporting_unit, survey, business_name) VALUES ("{0}", "test","test",' \
                        '"{1}", "ACollectionCase", "AReportingUnit", "BRES", "ABusiness")'.format(
                    msg_id, thread_id)
                con.execute(query)
                query = 'INSERT INTO status(label, msg_id, actor) VALUES("SENT", "{0}", "BRES")'.format(
                    msg_id)
                con.execute(query)
                query = 'INSERT INTO status(label, msg_id, actor) VALUES("INBOX", "{0}", "respondent.21345")' \
                    .format(msg_id)
                con.execute(query)
                query = 'INSERT INTO status(label, msg_id, actor) VALUES("UNREAD", "{0}", "respondent.21345")' \
                    .format(msg_id)
                con.execute(query)
                query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Sent", "{0}", "{1}")'.format(
                    msg_id, str(datetime(year, month, day + 1)))
                con.execute(query)
                query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Read", "{0}", "{1}")'.format(
                    msg_id, str(datetime(year, month, day + 2)))
                con.execute(query)

                if random.choice(range(0, no_of_threads)) == 1:
                    msg_id = str(uuid.uuid4())
                    query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                            ' collection_case, reporting_unit, survey, business_name) VALUES ("{0}", "test","test",' \
                            '"{1}", "ACollectionCase", "AReportingUnit", "BRES", "ABusiness")'.format(
                        msg_id, thread_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT_INBOX", "{0}", "respondent.21345")'.format(
                        msg_id)
                    con.execute(query)
                    query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT", "{0}",' \
                            ' "SurveyType")'.format(msg_id)
                    con.execute(query)
                    query = 'INSERT INTO events(event, msg_id, date_time) VALUES("Draft_Saved", "{0}", "{1}")'.format(
                        msg_id, str(datetime(year, month, day + 3)))
                    con.execute(query)

        return threads


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

    def test_all_message_returned_with_business_option(self):
        """retrieves all messages from database for user with business option"""
        self.populate_database(5, multiple_users=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             business='ABusiness')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['business_name'] == 'ABusiness')
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_business_option(self):
        """retrieves no messages from database for user with business option"""
        self.populate_database(5, multiple_users=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_message_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345',
                                                             business='AnotherBusiness')[1]
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['business_name'] == 'AnotherBusiness')
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

    def test_all_msg_returned_for_thread_id_with_draft(self):
        """retrieves messages for thread_id from database with draft """
        self.populate_database(3, add_reply=True, add_draft=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', 'internal.21345', _survey='SurveyType')
                self.assertEqual(len(response), 9)

    def test_all_msg_returned_for_thread_id_without_draft(self):
        """retrieves messages for thread_id from database without draft"""
        self.populate_database(3, add_reply=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', 'respondent.21345')
                self.assertEqual(len(response), 6)

    def test_all_msg_returned_for_thread_id_with_draft_inbox(self):
        """retrieves messages for thread_id from database with draft inbox"""
        self.populate_database(3, add_reply=True, add_draft=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', 'respondent.21345')
                self.assertEqual(len(response), 6)

    def test_thread_returned_in_desc_order(self):
        """check thread returned in correct order"""
        self.populate_database(3, add_reply=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', 'respondent.21345')
                self.assertEqual(len(response), 6)

                sent = []
                for message in response:
                    sent.append(message['sent_date'])

                desc_date = sorted(sent, reverse=True)
                self.assertEqual(len(sent), 6)
                self.assertListEqual(desc_date, sent)

    def test_thread_returned_in_desc_order_with_draft(self):
        """check thread returned in correct order with draft"""
        self.populate_database(3, add_reply=True, add_draft=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', 'internal.21345', _survey='SurveyType')
                self.assertEqual(len(response), 9)

                sent = []
                read = []
                modified = []
                date = []
                for message in response:
                    sent.append(message['sent_date'])
                    read.append(message['read_date'])
                    modified.append(message['modified_date'])

                for x in range(0, len(sent)):
                    if sent[x] != 'N/A':
                        date.append(sent[x])
                    else:
                        date.append(modified[x])

                desc_date = sorted(date, reverse=True)
                self.assertListEqual(desc_date, date)

    def test_retrieve_thread_raises_server_error(self):
        """retrieves messages when db does not exist"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().retrieve_thread('ThreadId', 'respondent.21345')

    def test_thread_returned_with_thread_id_returns_404(self):
        """retrieves thread using id that doesn't exist"""
        with app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_thread('anotherThreadId', 'respondent.21345')

    def test_retrieve_draft_raises_server_error(self):
        """retrieves draft when db does not exist"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().retrieve_draft('draftId', 'respondent.21345')

    def test_retrieve_thread_list_raises_server_error(self):
        """retrieves threads when db does not exist"""
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().retrieve_thread_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')

    def test_thread_list_returned_in_descending_order(self):
        """retrieves threads from database in desc sent_date order"""
        self.create_threads(5)
        self.populate_database(5, single=False, multiple_users=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]

                sent = []
                read = []
                modified = []
                thread_ids = []
                date = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    sent.append(serialized_msg['sent_date'])
                    read.append(serialized_msg['read_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    modified.append(serialized_msg['modified_date'])

                for x in range(0, len(sent)):
                    if sent[x] != 'N/A':
                        date.append(sent[x])
                    else:
                        date.append(modified[x])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_latest_message_from_each_thread_chosen_desc(self):
        """checks the message chosen for each thread is the latest message within that thread"""
        self.create_threads(5)
        self.populate_database(5, single=False, multiple_users=True)

        with app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread_list(1, MESSAGE_QUERY_LIMIT, 'respondent.21345')[1]

                sent = []
                read = []
                modified = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize('respondent.21345')
                    sent.append(serialized_msg['sent_date'])
                    read.append(serialized_msg['read_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    modified.append(serialized_msg['modified_date'])
                    msg_ids.append(serialized_msg['msg_id'])

                self.assertEqual(len(msg_ids), 5)

                for x in range(0,len(thread_ids)):
                    thread = Retriever().retrieve_thread(thread_ids[x], user_urn='respondent.21345')
                    self.assertEqual(sent[x], thread[0]['sent_date'])
                    self.assertEqual(msg_ids[x], thread[0]['msg_id'])
