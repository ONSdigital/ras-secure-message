import unittest
import uuid
from app.validation.domain import MessageSchema
from flask import current_app
from sqlalchemy import create_engine
from app.validation.labels import Labels
from app.application import app
from app.repository import database
from app.repository.modifier import Modifier
from app.repository.retriever import Retriever
from app.repository.saver import Saver
from unittest import mock


class ModifyTestCase(unittest.TestCase):
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
                query = 'INSERT INTO secure_message(id, msg_id, subject, body, thread_id, sent_date,' \
                        ' collection_case, reporting_unit, survey) VALUES ({0}, "{1}", "test","test","", ' \
                        '"2017-02-03 00:00:00", "ACollectionCase", "AReportingUnit", ' \
                        '"SurveyType")'.format(i, msg_id)
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

    def test_archived_label_is_added_to_message(self):
        """testing message is added to database with archived label attached"""
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
                message_service = Retriever()
                # pass msg_id and user urn
                message = message_service.retrieve_message(msg_id, 'respondent.21345')
                # Modifier.add_label(message,'respondent.21345')
                Modifier.add_archived(message, 'respondent.21345', )
                message = message_service.retrieve_message(msg_id, 'respondent.21345')
                self.assertCountEqual(message['labels'], ['SENT', 'ARCHIVE'])

    def test_archived_label_is_removed_from_message(self):
        """testing message is added to database with archived label removed and inbox and read is added instead"""
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
                message_service = Retriever()
                # pass msg_id and user urn
                message = message_service.retrieve_message(msg_id, 'respondent.21345')
                modifier = Modifier()
                modifier.add_archived(message, 'respondent.21345')
                message = message_service.retrieve_message(msg_id, 'respondent.21345')
                modifier.del_archived(message, 'respondent.21345', )
                message = message_service.retrieve_message(msg_id, 'respondent.21345')
                self.assertCountEqual(message['labels'], ['SENT'])

    def test_unread_label_is_removed_from_message(self):
        """testing message is added to database with archived label removed and inbox and read is added instead"""
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
                message_service = Retriever()
                # pass msg_id and user urn
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                modifier = Modifier()
                modifier.del_unread(message, 'internal.21345')
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                self.assertCountEqual(message['labels'], ['INBOX'])

    def test_unread_label_is_added_to_message(self):
        """testing message is added to database with archived label removed and inbox and read is added instead"""
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
                message_service = Retriever()
                # pass msg_id and user urn
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                modifier = Modifier()
                modifier.del_unread(message, 'internal.21345')
                modifier.add_unread(message, 'internal.21345')
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                self.assertCountEqual(message['labels'], ['UNREAD', 'INBOX'])

    def test_add_archive_is_added_to_internal(self):
        """testing message is added to database with archived label attached"""
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
                message_service = Retriever()
                # pass msg_id and user urn
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                Modifier.del_archived(message, 'internal.21345')
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                Modifier.add_archived(message, 'internal.21345')
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                self.assertCountEqual(message['labels'], ['UNREAD', 'INBOX', 'ARCHIVE'])

    def test_read_date_is_set(self):
        """testing message read_date is set when unread label is removed"""
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
                message_service = Retriever()
                modifier = Modifier()
                # pass msg_id and user urn
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                modifier.del_unread(message, 'internal.21345')
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                self.assertIsNotNone(message['read_date'])

    def test_read_date_is_not_reset(self):
        """testing message read_date is not reset when unread label is removed again"""
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
                message_service = Retriever()
                modifier = Modifier()
                # pass msg_id and user urn
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                modifier.del_unread(message, 'internal.21345')
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                read_date_set = message['read_date']
                modifier.add_unread(message, 'internal.21345')
                modifier.del_unread(message, 'internal.21345')
                message = message_service.retrieve_message(msg_id, 'internal.21345')
                self.assertEqual(message['read_date'], read_date_set)

    def test_draft_label_is_deleted(self):
        """Check draft label is deleted for message"""

        query_add_status = "INSERT INTO status (id, msg_id, actor, label) VALUES (1, 'test', 'test', '{0}')"\
            .format(Labels.DRAFT.value)

        with self.engine.connect() as con:
            con.execute(query_add_status)

        with app.app_context():
            with current_app.test_request_context():

                modifier = Modifier()
                self.test_message = {
                    'msg_id': 'test123',
                    'urn_to': 'internal.richard',
                    'urn_from': 'respondent.torrance',
                    'subject': 'MyMessage',
                    'body': 'hello',
                    'thread_id': '',
                    'collection_case': 'ACollectionCase',
                    'reporting_unit': 'AReportingUnit',
                    'survey': 'ACollectionInstrument'
                }

                message = MessageSchema().load(self.test_message)
                modifier.del_draft(message.data)

                query_check_for_draft = "SELECT * FROM status WHERE msg_id='{0}'"\
                    .format(self.test_message['msg_id'])

                with self.engine.connect() as con:
                    response = con.execute(query_check_for_draft)
                    for row in response:
                        self.assertTrue(row is None)

    def test_sent_label_is_added(self):
        self.populate_database(1)
        with self.engine.connect() as con:
            query = 'SELECT msg_id FROM secure_message LIMIT 1'

            query_x = con.execute(query)
            msg_id = []
            for row in query_x:
                msg_id.append(row[0])

        with app.app_context():
            with current_app.test_request_context():
                modifier = Modifier()
                self.test_message = {
                    'msg_id': msg_id[0],
                    'urn_to': 'richard',
                    'urn_from': 'torrance',
                    'subject': 'MyMessage',
                    'body': 'hello',
                    'thread_id': '',
                    'collection_case': 'ACollectionCase',
                    'reporting_unit': 'AReportingUnit',
                    'survey': 'ACollectionInstrument'
                }
                message = MessageSchema().load(self.test_message)
                modifier.add_sent(message.data)
                with self.engine.connect() as con:
                    query_check_sent = con.execute("SELECT * FROM status WHERE msg_id='{0}' AND label='{1}'"
                                                   .format(message.data.msg_id, Labels.SENT.value))

                    for row in query_check_sent:
                        self.assertTrue(row is not None)
                    query_check_sent_date = con.execute("SELECT * FROM secure_message WHERE msg_id='{0}'"
                                                        .format(message.data.msg_id))
                    for row in query_check_sent_date:
                        self.assertTrue(row['sent_date'] is not None)

    def test_inbox_and_unread_added(self):

        self.test_message = {
            'msg_id': 'test',
            'urn_to': 'richard',
            'urn_from': 'torrance',
            'subject': 'MyMessage',
            'body': 'hello',
            'thread_id': '',
            'collection_case': 'ACollectionCase',
            'reporting_unit': 'AReportingUnit',
            'survey': 'ACollectionInstrument'
        }
        with app.app_context():
            with current_app.test_request_context():
                message = MessageSchema().load(self.test_message)

                modifier = Modifier()

                modifier.add_inbox_and_unread_for_draft_remove_inbox_draft(message.data)

                with self.engine.connect() as con:
                    request = con.execute("SELECT * FROM status WHERE msg_id='{0}' AND label='{1}'"
                                          .format(self.test_message['msg_id'], Labels.INBOX.value))
                    self.assertTrue(request.returns_rows)
                    request_unread = con.execute("SELECT * FROM status WHERE msg_id='{0}' AND label='{1}'"
                                                 .format(self.test_message['msg_id'], Labels.UNREAD.value))
                    self.assertTrue(request_unread.returns_rows)


