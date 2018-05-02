import unittest
import uuid

from flask import current_app
from sqlalchemy import create_engine
from werkzeug.exceptions import InternalServerError

from secure_message import constants
from secure_message.application import create_app
from secure_message.common.eventsapi import EventsApi
from secure_message.repository import database
from secure_message.repository.modifier import Modifier
from secure_message.repository.retriever import Retriever
from secure_message.validation.user import User
from tests.app import test_utilities


class ModifyTestCaseHelper:
    """Helper class for Modify Tests"""

    def populate_database(self, record_count=0):
        """Adds a sppecified number of Messages to the db"""
        with self.engine.connect() as con:
            for i in range(record_count):
                msg_id = str(uuid.uuid4())
                query = f'''INSERT INTO securemessage.secure_message(id, msg_id, subject, body, thread_id,
                        collection_case, ru_id, collection_exercise, survey) VALUES ({i}, '{msg_id}', 'test','test','',
                        'ACollectionCase', 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ACollectionExercise',
                        'BRES')'''
                con.execute(query)
                query = f'''INSERT INTO securemessage.status(label, msg_id, actor) VALUES('SENT', '{msg_id}',
                        '0a7ad740-10d5-4ecb-b7ca-3c0384afb882')'''
                con.execute(query)
                query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('INBOX', '{msg_id}', 'BRES')"
                con.execute(query)
                query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('UNREAD', '{msg_id}', 'BRES')"
                con.execute(query)
                query = f'''INSERT INTO securemessage.events(event, msg_id, date_time)
                         VALUES('{EventsApi.SENT.value}', '{msg_id}', '2017-02-03 00:00:00')'''
                con.execute(query)
                query = f'''INSERT INTO securemessage.events(event, msg_id, date_time)
                        VALUES('{EventsApi.READ.value}', '{msg_id}', '2017-02-03 00:00:00')'''
                con.execute(query)


class ModifyTestCase(unittest.TestCase, ModifyTestCaseHelper):
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

        self.user_internal = User('ce12b958-2a5f-44f4-a6da-861e59070a31', 'internal')
        self.user_respondent = User('0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'respondent')

    def test_two_unread_labels_are_added_to_message(self):
        """testing duplicate message labels are not added to the database"""
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
                message_service = Retriever()
                message = message_service.retrieve_message(msg_id, self.user_internal)
                modifier = Modifier()
                modifier.add_unread(message, self.user_internal)
                modifier.add_unread(message, self.user_internal)
        with self.engine.connect() as con:
            query = f"SELECT count(label) FROM securemessage.status WHERE msg_id = '{msg_id}' AND label = 'UNREAD'"
            query_x = con.execute(query)
            unread_label_total = []
            for row in query_x:
                unread_label_total.append(row[0])
            self.assertTrue(unread_label_total[0] == 1)

    def test_read_date_is_set(self):
        """testing message read_date is set when unread label is removed"""
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
                message_service = Retriever()
                modifier = Modifier()
                message = message_service.retrieve_message(msg_id, self.user_internal)
                modifier.del_unread(message, self.user_internal)
                message = message_service.retrieve_message(msg_id, self.user_internal)
                self.assertIsNotNone(message['read_date'])

    def test_read_date_is_not_reset(self):
        """testing message read_date is not reset when unread label is removed again"""
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
                message_service = Retriever()
                modifier = Modifier()
                message = message_service.retrieve_message(msg_id, self.user_internal)
                modifier.del_unread(message, self.user_internal)
                message = message_service.retrieve_message(msg_id, self.user_internal)
                read_date_set = message['read_date']
                modifier.add_unread(message, self.user_internal)
                message = message_service.retrieve_message(msg_id, self.user_internal)
                modifier.del_unread(message, self.user_internal)
                message = message_service.retrieve_message(msg_id, self.user_internal)
                self.assertEqual(message['read_date'], read_date_set)

    def test_exception_for_add_label_raises(self):
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Modifier.add_label('UNREAD', {'survey': 'survey'}, self.user_internal)

    def test_exception_for_remove_label_raises(self):
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Modifier.remove_label('UNREAD', {'survey': 'survey'}, self.user_internal)

    def test_replace_current_recipient_status_raises(self):
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Modifier.replace_current_recipient_status(self.user_internal, 'Torrance')

    def test_get_label_actor_to_respondent(self):
        message_to_respondent = {'msg_id': 'test1',
                                 'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                                 'msg_from': 'ce12b958-2a5f-44f4-a6da-861e59070a31',
                                 'subject': 'MyMessage',
                                 'body': 'hello',
                                 'thread_id': '',
                                 'collection_case': 'ACollectionCase',
                                 'collection_exercise': 'ACollectionExercise',
                                 'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                 'survey': test_utilities.BRES_SURVEY,
                                 'from_internal': True}

        self.assertEqual(Modifier._get_label_actor(user=self.user_internal, message=message_to_respondent),
                         'ce12b958-2a5f-44f4-a6da-861e59070a31')
        self.assertEqual(Modifier._get_label_actor(user=self.user_respondent, message=message_to_respondent),
                         '0a7ad740-10d5-4ecb-b7ca-3c0384afb882')

    def test_get_label_actor_to_bres_user(self):
        user_bres = User(constants.BRES_USER, 'internal')
        message_to_bres = {'msg_id': 'test2',
                                     'msg_to': [constants.BRES_USER],
                                     'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                     'subject': 'MyMessage',
                                     'body': 'hello',
                                     'thread_id': '',
                                     'collection_case': 'ACollectionCase',
                                     'collection_exercise': 'ACollectionExercise',
                                     'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                     'survey': test_utilities.BRES_SURVEY,
                                     'from_internal': False}

        self.assertEqual(Modifier._get_label_actor(user=user_bres, message=message_to_bres),
                         constants.BRES_USER)
        self.assertEqual(Modifier._get_label_actor(user=self.user_internal, message=message_to_bres),
                         constants.BRES_USER)
        self.assertEqual(Modifier._get_label_actor(user=self.user_respondent, message=message_to_bres),
                         '0a7ad740-10d5-4ecb-b7ca-3c0384afb882')

    def test_get_label_actor_to_group(self):
        message_to_internal_group = {'msg_id': 'test3',
                                     'msg_to': [constants.NON_SPECIFIC_INTERNAL_USER],
                                     'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                     'subject': 'MyMessage',
                                     'body': 'hello',
                                     'thread_id': '',
                                     'collection_case': 'ACollectionCase',
                                     'collection_exercise': 'ACollectionExercise',
                                     'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                     'survey': test_utilities.BRES_SURVEY,
                                     'from_internal': False}

        self.assertEqual(Modifier._get_label_actor(user=self.user_internal, message=message_to_internal_group),
                         constants.NON_SPECIFIC_INTERNAL_USER)
        self.assertEqual(Modifier._get_label_actor(user=self.user_respondent, message=message_to_internal_group),
                         '0a7ad740-10d5-4ecb-b7ca-3c0384afb882')

    def test_get_label_actor_to_internal_user(self):
        message_to_internal_user = {'msg_id': 'test4',
                                    'msg_to': ['ce12b958-2a5f-44f4-a6da-861e59070a31'],
                                    'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                    'subject': 'MyMessage',
                                    'body': 'hello',
                                    'thread_id': '',
                                    'collection_case': 'ACollectionCase',
                                    'collection_exercise': 'ACollectionExercise',
                                    'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                    'survey': test_utilities.BRES_SURVEY,
                                    'from_internal': False}

        self.assertEqual(Modifier._get_label_actor(user=self.user_internal, message=message_to_internal_user),
                         'ce12b958-2a5f-44f4-a6da-861e59070a31')
        self.assertEqual(Modifier._get_label_actor(user=self.user_respondent, message=message_to_internal_user),
                         '0a7ad740-10d5-4ecb-b7ca-3c0384afb882')

    def test_get_label_actor_raises_exception_for_missing_fields(self):
        message_missing_fields = {'msg_id': 'test5',
                                  'subject': 'MyMessage',
                                  'body': 'hello',
                                  'thread_id': '',
                                  'collection_case': 'ACollectionCase',
                                  'collection_exercise': 'ACollectionExercise',
                                  'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                  'survey': test_utilities.BRES_SURVEY,
                                  'from_internal': False}

        with self.assertRaises(InternalServerError):
            Modifier._get_label_actor(user=self.user_internal, message=message_missing_fields)


if __name__ == '__main__':
    unittest.main()
