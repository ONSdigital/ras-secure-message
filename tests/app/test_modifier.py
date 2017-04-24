import unittest
import uuid

from flask import current_app
from sqlalchemy import create_engine

from app.application import app
from app.repository import database
from app.repository.modifier import Modifier
from app.repository.retriever import Retriever

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
                query = 'INSERT INTO secure_message(id, msg_id, subject, body, thread_id, sent_date, read_date,' \
                        ' collection_case, reporting_unit, survey) VALUES ({0}, "{1}", "test","test","", ' \
                        '"2017-02-03 00:00:00", "2017-02-03 00:00:00", "ACollectionCase", "AReportingUnit", ' \
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
                Modifier.add_archived(message, msg_id, 'respondent.21345')
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
                modifier.add_archived(message, msg_id, 'respondent.21345')
                message = message_service.retrieve_message(msg_id, 'respondent.21345')
                modifier.del_archived(message, msg_id, 'respondent.21345')
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
                modifier.del_unread(message, msg_id, 'internal.21345')
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
                modifier.del_unread(message, msg_id, 'internal.21345')
                modifier.add_unread(message, msg_id, 'internal.21345')
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
                    Modifier.add_archived(message, msg_id, 'internal.21345')
                    message = message_service.retrieve_message(msg_id, 'internal.21345')
                    self.assertCountEqual(message['labels'], ['SENT', 'ARCHIVE'])