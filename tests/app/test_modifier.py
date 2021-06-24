import datetime
import unittest
import uuid

from flask import current_app
from sqlalchemy import create_engine
from werkzeug.exceptions import InternalServerError

from secure_message import constants
from secure_message.application import create_app
from secure_message.common.eventsapi import EventsApi
from secure_message.repository import database
from secure_message.repository.database import SecureMessage
from secure_message.repository.modifier import Modifier
from secure_message.repository.retriever import Retriever
from secure_message.services.service_toggles import internal_user_service
from secure_message.validation.user import User


class ModifyTestCaseHelper:
    """Helper class for Modify Tests"""

    BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"

    def populate_database(self, record_count=0, mark_as_read=True):
        """Adds a specified number of Messages to the db in a single thread"""
        thread_id = str(uuid.uuid4())
        with self.engine.connect() as con:
            for i in range(record_count):
                msg_id = str(uuid.uuid4())
                # Only the first message in a thread needs a entry in the conversation table
                if i == 0:
                    query = f'''INSERT INTO securemessage.conversation(id, is_closed, closed_by, closed_by_uuid) VALUES('{thread_id}', false, '', '')'''
                    con.execute(query)
                query = f'''INSERT INTO securemessage.secure_message(id, msg_id, subject, body, thread_id,
                        case_id, business_id, exercise_id, survey_id) VALUES ({i}, '{msg_id}', 'test','test','{thread_id}',
                        'ACollectionCase', 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ACollectionExercise',
                        '{constants.NON_SPECIFIC_INTERNAL_USER}')'''
                con.execute(query)
                query = f'''INSERT INTO securemessage.status(label, msg_id, actor) VALUES('SENT', '{msg_id}',
                        '0a7ad740-10d5-4ecb-b7ca-3c0384afb882')'''
                con.execute(query)
                query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('INBOX', '{msg_id}', " \
                        f"'{constants.NON_SPECIFIC_INTERNAL_USER}')"
                con.execute(query)
                query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('UNREAD', '{msg_id}'," \
                        f"'{constants.NON_SPECIFIC_INTERNAL_USER}')"
                con.execute(query)
                query = f'''INSERT INTO securemessage.events(event, msg_id, date_time)
                         VALUES('{EventsApi.SENT.value}', '{msg_id}', '2017-02-03 00:00:00')'''
                con.execute(query)
                if mark_as_read:
                    query = f'''INSERT INTO securemessage.events(event, msg_id, date_time)
                            VALUES('{EventsApi.READ.value}', '{msg_id}', '2017-02-03 00:00:00')'''
                    con.execute(query)

        return thread_id

    def create_conversation_with_respondent_as_unread(self, user, message_count=0):
        """Adds a specified number of Messages to the db in a single thread"""
        # we should not be inserting records into the db for a unit test but sadly without a greater rework its the only way
        thread_id = str(uuid.uuid4())
        with self.engine.connect() as con:
            for i in range(message_count):
                msg_id = str(uuid.uuid4())
                # Only the first message in a thread needs a entry in the conversation table
                if i == 0:
                    query = f'''INSERT INTO securemessage.conversation(id, is_closed, closed_by, closed_by_uuid) VALUES('{thread_id}', false, '', '')'''
                    con.execute(query)
                query = f'''INSERT INTO securemessage.secure_message(id, msg_id, subject, body, thread_id,
                        case_id, business_id, exercise_id, survey_id) VALUES ({i}, '{msg_id}', 'test','test','{thread_id}',
                        'ACollectionCase', 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc', 'ACollectionExercise',
                        '{user.user_uuid}')'''
                con.execute(query)
                query = f'''INSERT INTO securemessage.status(label, msg_id, actor) VALUES('SENT', '{msg_id}',
                        '{constants.NON_SPECIFIC_INTERNAL_USER}')'''
                con.execute(query)
                query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('INBOX', '{msg_id}', " \
                        f"'{user.user_uuid}')"
                con.execute(query)
                query = f"INSERT INTO securemessage.status(label, msg_id, actor) VALUES('UNREAD', '{msg_id}'," \
                        f" '{user.user_uuid}')"
                con.execute(query)
                query = f'''INSERT INTO securemessage.events(event, msg_id, date_time)
                         VALUES('{EventsApi.SENT.value}', '{msg_id}', '2020-11-20 00:00:00')'''
                con.execute(query)
        return thread_id

    def add_conversation(self, conversation_id=str(uuid.uuid4()), is_closed=False, closed_by='', closed_by_uuid='', closed_at=None):
        """ Populate the conversation table"""
        # If conversation created needs to be closed, values are generated for you.  These can be overrriden by passing them
        # into function (i.e., if you need a specific name, but don't care about anything else, then only pass in 'closed_by')
        if is_closed:
            if not closed_by:
                closed_by = "Some person"
            if not closed_by_uuid:
                closed_by_uuid = str(uuid.uuid4())
            if not closed_at:
                closed_at = datetime.datetime.utcnow()
        with self.engine.connect() as con:
            query = f'''INSERT INTO securemessage.conversation(id, is_closed, closed_by, closed_by_uuid, closed_at) VALUES('{conversation_id}',
                    '{is_closed}', '{closed_by}', '{closed_by_uuid}', '{closed_at}')'''
            con.execute(query)
        return conversation_id


class ModifyTestCase(unittest.TestCase, ModifyTestCaseHelper):
    """Test case for message retrieval"""

    def setUp(self):
        """setup test environment"""

        self.app = create_app(config='TestConfig')

        self.app.testing = True
        self.engine = create_engine(self.app.config['SQLALCHEMY_DATABASE_URI'])

        with self.app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        self.user_internal = User('ce12b958-2a5f-44f4-a6da-861e59070a31', 'internal')
        self.user_respondent = User('0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'respondent')

    def tearDown(self):
        self.engine.dispose()

    def test_all_messages_in_conversation_marked_unread(self):
        # create a thread with two messages
        conversation_id = self.create_conversation_with_respondent_as_unread(user=self.user_respondent, message_count=2)
        with self.app.app_context():
            conversation = Retriever.retrieve_thread(conversation_id, self.user_respondent)
            for msg in conversation.all():
                # as there's two ways that a message is unread, first check the `read at` time isn't set
                self.assertIsNone(msg.read_at)
                # now collect all the message labels
                labels = []
                for status in msg.statuses:
                    labels.append(status.label)
                # and check the unread is present
                self.assertTrue("UNREAD" in labels)
            # now mark the first message as read and check the whole conversation is now read
            Modifier.mark_message_as_read(conversation[0].serialize(self.user_respondent), self.user_respondent)
            con = Retriever.retrieve_thread(conversation_id, self.user_respondent)
            for msg in con.all():
                # message `read at` should now be set
                self.assertIsNotNone(msg.read_at)
                # collect the labels again
                labels = []
                for status in msg.statuses:
                    labels.append(status.label)
                # and there should be no unread
                self.assertFalse("UNREAD" in labels)

    def test_close_conversation(self):
        """Test close conversation works"""
        conversation_id = self.populate_database(1)
        with self.app.app_context():
            internal_user_service.use_mock_service()
            # msg_id is the same as thread id for a conversation of 1
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)
            Modifier.close_conversation(metadata, self.user_internal)
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)

            self.assertTrue(metadata.is_closed)
            self.assertEqual(metadata.closed_by, "Selphie Tilmitt")
            self.assertEqual(metadata.closed_by_uuid, "ce12b958-2a5f-44f4-a6da-861e59070a31")
            self.assertTrue(isinstance(metadata.closed_at, datetime.datetime))
            # Test that timestamp on read message is less than 3 seconds old to prove it
            # was only just created
            delta = datetime.datetime.utcnow() - metadata.closed_at
            self.assertTrue(delta.total_seconds() < 3)

    def test_open_conversation(self):
        """Test re-opening conversation works"""
        conversation_id = self.add_conversation(is_closed=True)
        with self.app.app_context():
            # msg_id is the same as thread id for a conversation of 1
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)
            Modifier.open_conversation(metadata, self.user_internal)
            metadata = Retriever.retrieve_conversation_metadata(conversation_id)
            self.assertFalse(metadata.is_closed)
            self.assertIsNone(metadata.closed_by)
            self.assertIsNone(metadata.closed_by_uuid)
            self.assertIsNone(metadata.closed_at)

    def test_two_unread_labels_are_added_to_message(self):
        """testing duplicate message labels are not added to the database"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = con.execute('SELECT msg_id FROM securemessage.secure_message LIMIT 1')
            msg_id = query.first()[0]
        with self.app.app_context():
            with current_app.test_request_context():
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                Modifier.add_unread(message, self.user_internal)
                Modifier.add_unread(message, self.user_internal)
        with self.engine.connect() as con:
            query = f"SELECT count(label) FROM securemessage.status WHERE msg_id = '{msg_id}' AND label = 'UNREAD'"
            query_x = con.execute(query)
            unread_label_total = []
            for row in query_x:
                unread_label_total.append(row[0])
            self.assertTrue(unread_label_total[0] == 1)

    def test_read_date_is_set(self):
        """testing message read_date is set when unread label is removed"""
        thread_id = self.populate_database(1, mark_as_read=False)
        with self.app.app_context():
            thread = Retriever.retrieve_thread(thread_id, self.user_respondent).all()
            serialised_message = Retriever.retrieve_message(thread[0].msg_id, self.user_internal)
            Modifier.mark_message_as_read(serialised_message, self.user_internal)
            serialised_message = Retriever.retrieve_message(thread[0].msg_id, self.user_internal)
            db_message = SecureMessage.query.filter(SecureMessage.msg_id == serialised_message['msg_id']).one()

            self.assertIsNotNone(serialised_message['read_date'])
            self.assertTrue(isinstance(db_message.read_at, datetime.datetime))
            # Test that timestamp on read message is less than 3 seconds old to prove it
            # was only just created
            delta = datetime.datetime.utcnow() - db_message.read_at
            self.assertTrue(delta.total_seconds() < 3)

    def test_read_date_is_not_reset(self):
        """testing message read_date is not reset when unread label is removed again"""
        self.populate_database(1)
        with self.engine.connect() as con:
            query = con.execute('SELECT msg_id FROM securemessage.secure_message LIMIT 1')
            msg_id = query.first()[0]
        with self.app.app_context():
            with current_app.test_request_context():
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                Modifier.mark_message_as_read(message, self.user_internal)
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                read_date_set = message['read_date']
                Modifier.add_unread(message, self.user_internal)
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                Modifier.mark_message_as_read(message, self.user_internal)
                message = Retriever.retrieve_message(msg_id, self.user_internal)
                self.assertEqual(message['read_date'], read_date_set)

    def test_exception_for_add_label_raises(self):
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Modifier.add_label('UNREAD', {'survey_id': 'survey_id'}, self.user_internal)

    def test_exception_for_remove_label_raises(self):
        with self.app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Modifier.remove_label('UNREAD', {'survey_id': 'survey_id'}, self.user_internal)

    def test_get_label_actor_to_respondent(self):
        message_to_respondent = {'msg_id': 'test1',
                                 'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                                 'msg_from': 'ce12b958-2a5f-44f4-a6da-861e59070a31',
                                 'subject': 'MyMessage',
                                 'body': 'hello',
                                 'thread_id': '',
                                 'case_id': 'ACollectionCase',
                                 'exercise_id': 'ACollectionExercise',
                                 'business_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                 'survey_id': self.BRES_SURVEY,
                                 'from_internal': True}

        self.assertEqual(Modifier._get_label_actor(user=self.user_internal, message=message_to_respondent),
                         'ce12b958-2a5f-44f4-a6da-861e59070a31')
        self.assertEqual(Modifier._get_label_actor(user=self.user_respondent, message=message_to_respondent),
                         '0a7ad740-10d5-4ecb-b7ca-3c0384afb882')

    def test_get_label_actor_to_group(self):
        message_to_internal_group = {'msg_id': 'test3',
                                     'msg_to': [constants.NON_SPECIFIC_INTERNAL_USER],
                                     'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                     'subject': 'MyMessage',
                                     'body': 'hello',
                                     'thread_id': '',
                                     'case_id': 'ACollectionCase',
                                     'exercise_id': 'ACollectionExercise',
                                     'business_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                     'survey_id': self.BRES_SURVEY,
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
                                    'case_id': 'ACollectionCase',
                                    'exercise_id': 'ACollectionExercise',
                                    'business_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                    'survey_id': self.BRES_SURVEY,
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
                                  'case_id': 'ACollectionCase',
                                  'exercise_id': 'ACollectionExercise',
                                  'business_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                  'survey_id': self.BRES_SURVEY,
                                  'from_internal': False}

        with self.assertRaises(InternalServerError):
            Modifier._get_label_actor(user=self.user_internal, message=message_missing_fields)


if __name__ == '__main__':
    unittest.main()
