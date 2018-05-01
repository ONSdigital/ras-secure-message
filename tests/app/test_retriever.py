import unittest
import uuid
from datetime import datetime

from flask import current_app
from sqlalchemy import create_engine
from werkzeug.exceptions import NotFound

from secure_message.application import create_app
from secure_message.common.eventsapi import EventsApi
from secure_message.repository import database
from secure_message.repository.retriever import Retriever
from secure_message.constants import MESSAGE_QUERY_LIMIT
from secure_message.services.service_toggles import party
from secure_message import constants
from secure_message.validation.user import User
from tests.app.test_utilities import BRES_SURVEY, get_args


class RetrieverTestCaseHelper:

    default_internal_actor = 'internal_actor'
    default_external_actor = 'external_actor'

    """Helper class for Retriever Tests"""
    def add_secure_message(self, msg_id, subject="test", body="test", thread_id="ThreadId",
                           collection_case="ACollectionCase", ru_id="f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
                           survey=BRES_SURVEY, collection_exercise='CollectionExercise', from_internal=False):

        """ Populate the secure_message table"""

        with self.engine.connect() as con:
            query = f'''INSERT INTO securemessage.secure_message(msg_id, subject, body, thread_id,
                    collection_case, ru_id, survey, collection_exercise, from_internal) VALUES ('{msg_id}', '{subject}','{body}',
                    '{thread_id}', '{collection_case}', '{ru_id}', '{survey}', '{collection_exercise}', '{from_internal}')'''
            con.execute(query)

    def add_status(self, label, msg_id, actor):
        """ Populate the status table"""

        with self.engine.connect() as con:
            query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('{label}', '{msg_id}', '{actor}')"
            con.execute(query)

    def add_event(self, event, msg_id, date_time):
        """ Populate the event table"""

        with self.engine.connect() as con:
            query = f"INSERT INTO securemessage.events(event, msg_id, date_time) VALUES('{event}', '{msg_id}', '{date_time}')"
            con.execute(query)

    def del_status(self, label, msg_id, actor):
        """ Delete a specific row from status table"""

        with self.engine.connect() as con:
            query = f"DELETE FROM securemessage.status WHERE label = '{label}' AND msg_id = '{msg_id}' AND actor = '{actor}'"
            con.execute(query)

    def populate_database(self, no_of_messages=0, single=True, add_reply=False, add_draft=False, multiple_users=False,
                          external_actor=default_external_actor,
                          internal_actor=default_internal_actor):
        """ Populate the db with a specified number of messages and optionally replies , multiple users"""

        year = 2016
        month = 1
        day = 1

        for _ in range(no_of_messages):
            if day < 22:
                day += 1
            elif month < 12:
                day = 1
                month += 1
            else:
                day = 1
                month = 1
                year += 1

            if single:
                msg_id = str(uuid.uuid4())
                self.add_secure_message(msg_id=msg_id, from_internal=False)
                self.add_status(label="SENT", msg_id=msg_id, actor=external_actor)
                self.add_status(label="INBOX", msg_id=msg_id, actor=internal_actor)
                self.add_status(label="UNREAD", msg_id=msg_id, actor=internal_actor)

                self.add_event(event=EventsApi.SENT.value, msg_id=msg_id, date_time=datetime(year, month, day))
                day = day + 1

            if add_reply:
                self.del_status(label="UNREAD", msg_id=msg_id, actor=internal_actor)
                self.add_event(event=EventsApi.READ.value, msg_id=msg_id, date_time=datetime(year, month, day))
                day = day + 1
                msg_id = str(uuid.uuid4())
                self.add_secure_message(msg_id=msg_id, from_internal=True)
                self.add_status(label="SENT", msg_id=msg_id, actor=internal_actor)
                self.add_status(label="INBOX", msg_id=msg_id, actor=external_actor)
                self.add_status(label="UNREAD", msg_id=msg_id, actor=external_actor)

                self.add_event(event=EventsApi.SENT.value, msg_id=msg_id, date_time=datetime(year, month, day))
                day = day + 1

            if add_draft:
                msg_id = str(uuid.uuid4())
                self.add_secure_message(msg_id=msg_id, from_internal=True)
                self.add_status(label="DRAFT_INBOX", msg_id=msg_id, actor=external_actor)
                self.add_status(label="DRAFT", msg_id=msg_id, actor=internal_actor)

                self.add_event(event=EventsApi.DRAFT_SAVED.value, msg_id=msg_id, date_time=datetime(year, month, day))
                day = day + 1

            if multiple_users:
                msg_id = str(uuid.uuid4())
                self.add_secure_message(msg_id=msg_id, thread_id="AnotherThreadId",
                                        collection_case="AnotherCollectionCase", collection_exercise="AnotherCollectionExercise",
                                        ru_id='0a6018a0-3e67-4407-b120-780932434b36', survey="AnotherSurvey", from_internal=False)
                self.add_status(label="SENT", msg_id=msg_id, actor="1a7ad740-10d5-4ecb-b7ca-fb8823c0384a")
                self.add_status(label="INBOX", msg_id=msg_id, actor="11111111-10d5-4ecb-b7ca-fb8823c0384a")
                self.add_status(label="UNREAD", msg_id=msg_id, actor="11111111-10d5-4ecb-b7ca-fb8823c0384a")

                self.add_event(event=EventsApi.SENT.value, msg_id=msg_id, date_time=datetime(year, month, day))
                day = day + 1

    def create_threads(self, no_of_threads=1, add_internal_draft=False, add_respondent_draft=False,
                       external_actor=default_external_actor,
                       internal_actor=default_internal_actor):
        """ Populate the db with a specified number of messages and optionally replies , multiple users"""
        threads = []
        year = 2016
        month = 1
        day = 1

        for _ in range(no_of_threads):
            if day < 22:
                day += 1
            elif month < 12:
                day = 1
                month += 1
            else:
                day = 1
                month = 1
                year += 1

            msg_id = str(uuid.uuid4())
            thread_id = msg_id
            threads.append(thread_id)
            self.add_secure_message(msg_id=msg_id, thread_id=thread_id, survey=constants.BRES_USER, from_internal=False)
            self.add_status(label="SENT", msg_id=msg_id, actor=external_actor)
            self.add_status(label="INBOX", msg_id=msg_id, actor=internal_actor)

            self.add_event(event=EventsApi.SENT.value, msg_id=msg_id, date_time=datetime(year, month, day))
            day += 1
            self.add_event(event=EventsApi.READ.value, msg_id=msg_id, date_time=datetime(year, month, day))
            day += 1
            msg_id = str(uuid.uuid4())
            self.add_secure_message(msg_id=msg_id, thread_id=thread_id, survey=constants.BRES_USER, from_internal=True)
            self.add_status(label="SENT", msg_id=msg_id, actor=internal_actor)
            self.add_status(label="UNREAD", msg_id=msg_id, actor=external_actor)
            self.add_status(label="INBOX", msg_id=msg_id, actor=external_actor)
            self.add_event(event=EventsApi.SENT.value, msg_id=msg_id, date_time=datetime(year, month, day))
            day += 1

            last_msg_id = msg_id

            if add_internal_draft:  # adds draft from internal
                msg_id = str(uuid.uuid4())
                self.add_secure_message(msg_id=msg_id, thread_id=thread_id, survey=constants.BRES_USER, from_internal=True)
                self.add_status(label="DRAFT_INBOX", msg_id=msg_id, actor=external_actor)
                self.add_status(label="DRAFT", msg_id=msg_id, actor=internal_actor)

                self.add_event(event=EventsApi.DRAFT_SAVED.value, msg_id=msg_id, date_time=datetime(year, month, day))
                day += 1

            if add_respondent_draft:  # adds draft from respondent

                self.del_status(label="UNREAD", msg_id=last_msg_id, actor=RetrieverTestCaseHelper.default_external_actor)
                self.add_event(event=EventsApi.READ.value, msg_id=last_msg_id, date_time=datetime(year, month, day))
                day += 1
                msg_id = str(uuid.uuid4())
                self.add_secure_message(msg_id=msg_id, thread_id=thread_id, survey=constants.BRES_USER, from_internal=False)
                self.add_status(label="DRAFT_INBOX", msg_id=msg_id, actor=internal_actor)
                self.add_status(label="DRAFT", msg_id=msg_id, actor=external_actor)

                self.add_event(event=EventsApi.DRAFT_SAVED.value, msg_id=msg_id, date_time=datetime(year, month, day))
                day += 1
        return threads


class RetrieverTestCase(unittest.TestCase, RetrieverTestCaseHelper):
    """Test case for message retrieval"""
    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True
        self.engine = create_engine(self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.MESSAGE_LIST_ENDPOINT = "http://localhost:5050/messages"
        self.MESSAGE_BY_ID_ENDPOINT = "http://localhost:5050/message/"
        with self.app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        self.user_internal = User(RetrieverTestCaseHelper.default_internal_actor, 'internal')
        self.user_respondent = User(RetrieverTestCaseHelper.default_external_actor, 'respondent')
        party.use_mock_service()
        self.app.config['NOTIFY_CASE_SERVICE'] = '1'

    def test_0_msg_returned_when_db_empty_true(self):
        """retrieves messages from empty database"""
        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    msg.append(message.serialize)
                self.assertEqual(msg, [])

    def test_all_msg_returned_when_db_less_than_limit(self):
        """retrieves messages from database with less entries than retrieval amount"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    msg.append(message.serialize)
                self.assertEqual(len(msg), 5)

    def test_msg_limit_returned_when_db_greater_than_limit(self):
        """retrieves x messages when database has greater than x entries"""
        self.populate_database(MESSAGE_QUERY_LIMIT + 5)
        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)
                result = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in result.items:
                    serialized_message = message.serialize(self.user_respondent)
                    msg.append(serialized_message)
                self.assertEqual(len(msg), MESSAGE_QUERY_LIMIT)

    def test_msg_and_not_drafts_returned(self):
        """retrieves messages not drafts"""
        self.populate_database(5, add_draft=True)
        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, surveys=[BRES_SURVEY])
                result = Retriever().retrieve_message_list(self.user_internal, args)
                msg = []
                for message in result.items:
                    serialized_message = message.serialize(self.user_internal)
                    msg.append(serialized_message)
                self.assertEqual(len(msg), 10)

    def test_msg_limit_returned_when_db_greater_than_limit_with_replies(self):
        """retrieves x messages when database has greater than x entries and database has reply messages"""
        self.populate_database(MESSAGE_QUERY_LIMIT + 5, multiple_users=True, add_reply=True)
        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)
                result = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in result.items:
                    serialized_message = message.serialize(self.user_respondent)
                    msg.append(serialized_message)
                self.assertEqual(len(msg), MESSAGE_QUERY_LIMIT)

    def test_msg_limit_returned_when_db_greater_than_limit_with_replies_drafts(self):
        """retrieves x messages when database has greater than x entries and database has reply messages and drafts"""
        self.populate_database(MESSAGE_QUERY_LIMIT + 5, multiple_users=True, add_reply=True, add_draft=True)
        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)
                result = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in result.items:
                    serialized_message = message.serialize(self.user_respondent)
                    msg.append(serialized_message)
                self.assertEqual(len(msg), MESSAGE_QUERY_LIMIT)

    def test_msg_returned_with_msg_id_true(self):
        """retrieves message using id"""
        self.populate_database(20)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_internal)
                    self.assertEqual(response['msg_id'], str(names[0]))

    def test_msg_returned_with_msg_id_returns_404(self):
        """retrieves message using id that doesn't exist"""
        message_id = "1"
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id, self.user_internal)

    def test_msg_returned_with_msg_id_msg_not_in_database(self):
        """retrieves message using id"""
        message_id = "21"
        self.populate_database(20)
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id, self.user_internal)

    def test_correct_labels_returned_internal(self):
        """retrieves message using id and checks the labels are correct"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_internal)
                    labels = ['INBOX', 'UNREAD']
                    self.assertCountEqual(response['labels'], labels)

    def test_correct_labels_returned_external(self):
        """retrieves message using id and checks the labels are correct"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_respondent)
                    labels = ['SENT']
                    self.assertCountEqual(response['labels'], labels)

    def test_correct_to_and_from_returned_BRES_user(self):
        """retrieves message using id and checks the to and from urns are correct"""
        self.populate_database(1, internal_actor=constants.BRES_USER)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_respondent)
                    msg_to = [constants.BRES_USER]
                    self.assertEqual(response['msg_to'], msg_to)
                    self.assertEqual(response['msg_from'], self.user_respondent.user_uuid)

    def test_correct_to_and_from_returned_not_BRES_user(self):
        """retrieves message using id and checks the to and from urns are correct"""
        self.populate_database(1, internal_actor=self.user_internal.user_uuid)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_respondent)
                    self.assertEqual(response['msg_to'][0], self.user_internal.user_uuid)
                    self.assertEqual(response['msg_from'], self.user_respondent.user_uuid)

    def test_all_draft_message_returned(self):
        """retrieves messages from database with label DRAFT for user"""
        self.populate_database(5, add_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, surveys=[BRES_SURVEY], label='DRAFT')
                response = Retriever().retrieve_message_list(self.user_internal, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    msg.append(serialized_msg)
                    self.assertTrue('DRAFT' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_sent_message_returned(self):
        """retrieves messages from database with label SENT for user"""
        self.populate_database(5, add_reply=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, label='SENT')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue('SENT' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_inbox_message_returned(self):
        """retrieves messages from database with label SENT for user"""
        self.populate_database(5, add_reply=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, surveys=[BRES_SURVEY], label='INBOX')
                response = Retriever().retrieve_message_list(self.user_internal, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    msg.append(serialized_msg)
                    self.assertTrue('INBOX' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_message_returned_no_label_option(self):
        """retrieves all messages from database for user with no messages with label DRAFT_INBOX"""
        self.populate_database(5, add_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_message_list(self.user_respondent, args)

                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertFalse('DRAFT_INBOX' in serialized_msg['labels'])
                self.assertEqual(len(msg), 5)

    def test_all_message_returned_with_ru_option(self):
        """retrieves all messages from database for user with ru option"""
        self.populate_database(5, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, ru='f1a5e99c-8edf-489a-9c72-6cabe6c387fc')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['ru_id'] == 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc')
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_ru_option(self):
        """retrieves no messages from database for user with ru option"""
        self.populate_database(5, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, ru='0a6018a0-3e67-4407-b120-780932434b36')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['ru_id'] == '0a6018a0-3e67-4407-b120-780932434b36')
                self.assertEqual(len(msg), 0)

    def test_all_message_returned_with_survey_option(self):
        """retrieves all messages from database for user with survey option"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, surveys=[BRES_SURVEY])
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['survey'] == BRES_SURVEY)
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_survey_option(self):
        """retrieves no messages from database for user with survey option"""
        self.populate_database(5, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, surveys='AnotherSurvey')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['survey'] == 'AnotherSurvey')
                self.assertEqual(len(msg), 0)

    def test_all_message_returned_with_cc_option(self):
        """retrieves all messages from database for user with cc option"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, cc='ACollectionCase')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['collection_case'] == 'ACollectionCase')
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_cc_option(self):
        """retrieves no messages from database for user with cc option"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, cc='AnotherCollectionCase')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['collection_case'] == 'AnotherCollectionCase')
                self.assertEqual(len(msg), 0)

    def test_all_message_returned_with_ce_option(self):
        """retrieves all messages from database for user with ce option"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, ce='CollectionExercise')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['collection_exercise'] == 'CollectionExercise')
                self.assertEqual(len(msg), 5)

    def test_no_message_returned_with_ce_option(self):
        """retrieves no messages from database for user with ce option"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, ce='AnotherCollectionExercise')
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                msg = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    msg.append(serialized_msg)
                    self.assertTrue(serialized_msg['collection_exercise'] == 'AnotherCollectionExercise')
                self.assertEqual(len(msg), 0)

    def test_message_list_returned_in_descending_order(self):
        """retrieves messages from database in desc sent_date order"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, desc=True)
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_message_list_returned_in_ascending_order(self):
        """retrieves messages from database in asc sent_date order"""
        self.populate_database(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, desc=False)
                response = Retriever().retrieve_message_list(self.user_respondent, args)
                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                asc_date = sorted(date, reverse=False)
                self.assertEqual(len(date), 5)
                self.assertListEqual(asc_date, date)

    def test_message_list_returned_in_ascending_order_not_drafts(self):
        """retrieves messages and drafts from database in asc sent_date order"""
        self.populate_database(5, add_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, surveys=[BRES_SURVEY], desc=False)
                response = Retriever().retrieve_message_list(self.user_internal, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                asc_date = sorted(date, reverse=False)
                self.assertEqual(len(date), 10)
                self.assertListEqual(asc_date, date)

    def test_messages_list_returned_in_descending_order_not_drafts(self):
        """retrieves messages and drafts from database in desc sent_date order"""
        self.populate_database(5, add_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT, surveys=[BRES_SURVEY], desc=True)
                response = Retriever().retrieve_message_list(self.user_internal, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 10)
                self.assertListEqual(desc_date, date)

    def test_sent_date_returned_for_message(self):
        """retrieves message using id and checks the sent date returned"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_internal)
                    self.assertTrue('modified_date' not in response)
                    self.assertTrue(response['sent_date'] != "N/A")

    def test_read_date_returned_for_message(self):
        """retrieves message using id and checks the read date returned"""
        self.populate_database(1, add_reply=True)
        with self.engine.connect() as con:
            query = "SELECT securemessage.secure_message.msg_id FROM securemessage.secure_message " \
                    "JOIN securemessage.events ON securemessage.secure_message.msg_id = securemessage.events.msg_id " \
                    "WHERE securemessage.events.event = '" + EventsApi.READ.value + "' LIMIT 1"
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])
            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_internal)
                    self.assertTrue('modified_date' not in response)
                    self.assertTrue(response['read_date'] != "N/A")

    def test_draft_returned_with_msg_id_draft_not_in_database(self):
        """retrieves draft using id where draft not in database"""
        message_id = str(uuid.uuid4())
        self.populate_database(1, single=False, add_draft=True)
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_message(message_id, self.user_internal)

    def test_correct_labels_returned_for_draft(self):
        """retrieves draft using id and checks the labels are correct"""
        self.populate_database(1, single=False, add_draft=True)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_internal)
                    labels = ['DRAFT']
                    self.assertCountEqual(response['labels'], labels)

    def test_correct_to_and_from_returned_for_draft(self):
        """retrieves draft using id and checks the to and from urns are correct"""
        self.populate_database(1, single=False, add_draft=True, internal_actor=self.user_internal.user_uuid)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM securemessage.secure_message LIMIT 1'
            query_x = con.execute(query)
            names = []
            for row in query_x:
                names.append(row[0])

            with self.app.app_context():
                with current_app.test_request_context():
                    msg_id = str(names[0])
                    response = Retriever().retrieve_message(msg_id, self.user_internal)
                    self.assertEqual(response['msg_to'], [self.user_respondent.user_uuid])
                    self.assertEqual(response['msg_from'], self.user_internal.user_uuid)

    def test_all_msg_returned_for_thread_id_with_draft(self):
        """retrieves messages for thread_id from database with draft """
        self.populate_database(3, add_reply=True, add_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', self.user_internal)
                self.assertEqual(len(response.all()), 9)

    def test_all_msg_returned_for_thread_id_without_draft(self):
        """retrieves messages for thread_id from database without draft"""
        self.populate_database(3, add_reply=True)

        with self.app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', self.user_respondent)
                self.assertEqual(len(response.all()), 6)

    def test_all_msg_returned_for_thread_id_with_draft_inbox(self):
        """retrieves messages for thread_id from database with draft inbox"""
        self.populate_database(3, add_reply=True, add_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', self.user_respondent)
                self.assertEqual(len(response.all()), 6)

    def test_thread_returned_in_desc_order(self):
        """check thread returned in correct order"""
        self.populate_database(3, add_reply=True)

        with self.app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', self.user_respondent)
                self.assertEqual(len(response.all()), 6)

                sent = [str(message.events[0].date_time) for message in response.all()]

                desc_date = sorted(sent, reverse=True)
                self.assertEqual(len(sent), 6)
                self.assertListEqual(desc_date, sent)

    def test_thread_returned_in_desc_order_with_draft(self):
        """check thread returned in correct order with draft"""
        self.populate_database(3, add_reply=True, add_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                response = Retriever().retrieve_thread('ThreadId', self.user_internal)
                self.assertEqual(len(response.all()), 9)

                date = [str(message.events[0].date_time) for message in response.all()]

                desc_date = sorted(date, reverse=True)
                self.assertListEqual(desc_date, date)

    def test_thread_returned_with_thread_id_returns_404(self):
        """retrieves thread using id that doesn't exist"""
        with self.app.app_context():
            with current_app.test_request_context():
                with self.assertRaises(NotFound):
                    Retriever().retrieve_thread('anotherThreadId', self.user_respondent)

    def test_thread_list_returned_in_descending_order_respondent(self):
        """retrieves threads from database in desc sent_date order for respondent"""
        self.create_threads(5)
        self.populate_database(5, single=False, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_respondent, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_thread_list_returned_in_descending_order_internal(self):
        """retrieves threads from database in desc sent_date order for internal user"""
        self.create_threads(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_internal, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_thread_list_returned_in_descending_order_respondent_with_draft(self):
        """retrieves threads from database in desc sent_date order for respondent with draft"""
        self.create_threads(5, add_respondent_draft=True)
        self.populate_database(5, single=False, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_respondent, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_thread_list_returned_in_descending_order_internal_with_draft(self):
        """retrieves threads from database in desc sent_date order for internal user with draft"""
        self.create_threads(5, add_internal_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_internal, args)

                date = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])

                desc_date = sorted(date, reverse=True)
                self.assertEqual(len(date), 5)
                self.assertListEqual(desc_date, date)

    def test_latest_message_from_each_thread_chosen_desc(self):
        """checks the message chosen for each thread is the latest message within that thread"""
        self.create_threads(5)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_internal, args)

                date = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    msg_ids.append(serialized_msg['msg_id'])

                self.assertEqual(len(msg_ids), 5)

                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)

                for x in range(0, len(thread_ids)):
                    thread = Retriever().retrieve_thread(thread_ids[x], self.user_internal)
                    self.assertEqual(date[x], str(thread.all()[0].events[0].date_time))
                    self.assertEqual(msg_ids[x], thread.all()[0].events[0].msg_id)

    def test_latest_message_from_each_thread_chosen_desc_respondent_with_respondent_draft(self):
        """checks the message chosen for each thread is the latest message within that thread
         for respondent with respondent drafts"""
        self.create_threads(5, add_respondent_draft=True)
        self.populate_database(5, single=False, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_respondent, args)

                date = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    msg_ids.append(serialized_msg['msg_id'])

                self.assertEqual(len(msg_ids), 5)

                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)

                for x in range(0, len(thread_ids)):
                    thread = Retriever().retrieve_thread(thread_ids[x], self.user_respondent)
                    self.assertEqual(date[x], str(thread.all()[0].events[0].date_time))
                    self.assertEqual(msg_ids[x], thread.all()[0].events[0].msg_id)

    def test_latest_message_from_each_thread_chosen_desc_internal_with_respondent_draft(self):
        """checks the message chosen for each thread is the latest message within that thread
        for internal user with respondent drafts"""
        self.create_threads(5, add_respondent_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_internal, args)

                date = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    msg_ids.append(serialized_msg['msg_id'])

                self.assertEqual(len(msg_ids), 5)

                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)

                for x in range(0, len(thread_ids)):
                    thread = Retriever().retrieve_thread(thread_ids[x], self.user_internal)
                    self.assertEqual(date[x], str(thread.all()[0].events[0].date_time))
                    self.assertEqual(msg_ids[x], thread.all()[0].events[0].msg_id)

    def test_latest_message_from_each_thread_chosen_desc_respondent_with_internal_draft(self):
        """checks the message chosen for each thread is the latest message within that thread
         for respondent with internal drafts"""
        self.create_threads(5, add_internal_draft=True)
        self.populate_database(5, single=False, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_respondent, args)

                date = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    msg_ids.append(serialized_msg['msg_id'])

                self.assertEqual(len(msg_ids), 5)

                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)

                for x in range(0, len(thread_ids)):
                    thread = Retriever().retrieve_thread(thread_ids[x], self.user_respondent)
                    self.assertEqual(date[x], str(thread.all()[0].events[0].date_time))
                    self.assertEqual(msg_ids[x], thread.all()[0].events[0].msg_id)

    def test_latest_message_from_each_thread_chosen_desc_internal_with_internal_draft(self):
        """checks the message chosen for each thread is the latest message within that thread
        for internal user with internal drafts"""
        self.create_threads(5, add_internal_draft=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_internal, args)

                date = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_internal)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    msg_ids.append(serialized_msg['msg_id'])

                self.assertEqual(len(msg_ids), 5)

                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)

                for x in range(0, len(thread_ids)):
                    thread = Retriever().retrieve_thread(thread_ids[x], self.user_internal)
                    self.assertEqual(date[x], str(thread.all()[0].events[0].date_time))
                    self.assertEqual(msg_ids[x], thread.all()[0].events[0].msg_id)

    def test_latest_message_from_each_thread_chosen_desc_respondent_with_both_users_drafts(self):
        """checks the message chosen for each thread is the latest message within that thread
         for respondent with drafts from both users"""
        self.create_threads(5, add_internal_draft=True, add_respondent_draft=True)
        self.populate_database(5, single=False, multiple_users=True)

        with self.app.app_context():
            with current_app.test_request_context():
                args = get_args(limit=MESSAGE_QUERY_LIMIT)
                response = Retriever().retrieve_thread_list(self.user_respondent, args)

                date = []
                thread_ids = []
                msg_ids = []
                for message in response.items:
                    serialized_msg = message.serialize(self.user_respondent)
                    if 'sent_date' in serialized_msg:
                        date.append(serialized_msg['sent_date'])
                    elif 'modified_date' in serialized_msg:
                        date.append(serialized_msg['modified_date'])
                    thread_ids.append(serialized_msg['thread_id'])
                    msg_ids.append(serialized_msg['msg_id'])

                self.assertEqual(len(msg_ids), 5)

                args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)

                for x in range(0, len(thread_ids)):
                    thread = Retriever().retrieve_thread(thread_ids[x], self.user_respondent)
                    self.assertEqual(date[x], str(thread.all()[0].events[0].date_time))
                    self.assertEqual(msg_ids[x], thread.all()[0].events[0].msg_id)

    def test_latest_message_from_each_thread_chosen_desc_internal_with_both_users_drafts(self):
        """checks the message chosen for each thread is the latest message within that thread
        for internal user with drafts from both users"""
        self.create_threads(1, add_internal_draft=True, add_respondent_draft=True)

        with self.app.app_context():
            args = get_args(limit=MESSAGE_QUERY_LIMIT)
            response = Retriever().retrieve_thread_list(self.user_internal, args)

            date = []
            thread_ids = []
            msg_ids = []
            for message in response.items:
                serialized_msg = message.serialize(self.user_internal)
                if 'sent_date' in serialized_msg:
                    date.append(serialized_msg['sent_date'])
                elif 'modified_date' in serialized_msg:
                    date.append(serialized_msg['modified_date'])
                thread_ids.append(serialized_msg['thread_id'])
                msg_ids.append(serialized_msg['msg_id'])

            self.assertEqual(len(msg_ids), 1)

            args = get_args(page=1, limit=MESSAGE_QUERY_LIMIT)

            for x in range(0, len(thread_ids)):
                thread = Retriever().retrieve_thread(thread_ids[x], self.user_internal)
                self.assertEqual(date[x], str(thread.all()[0].events[0].date_time))
                self.assertEqual(msg_ids[x], thread.all()[0].events[0].msg_id)


if __name__ == '__main__':
    unittest.main()
