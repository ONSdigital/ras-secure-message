import unittest
from unittest import mock
from app import application
from app import settings
from sqlalchemy import create_engine
from flask import json
from datetime import datetime, timezone
from app.application import app
from flask import current_app
from app.data_model import database
from app.common.alerts import AlertUser, AlertViaGovNotify


class FlaskTestCase(unittest.TestCase):
    """Test case for application endpoints"""\

    @classmethod
    def setUpClass(cls):
        app.testing = True

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """setup test environment"""
        self.app = application.app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db', echo=True)

        AlertUser.alertMethod = mock.Mock(AlertViaGovNotify)

        now = datetime.now(timezone.utc)
        self.test_message = {'msg_id': 'AMsgId',
                             'msg_to': 'richard',
                             'msg_from': 'torrance',
                             'subject': 'MyMessage',
                             'body': 'hello',
                             'thread_id': "",
                             'archive_status': False,
                             'read_status': False,
                             'sent_date': now,
                             'read_date': now,
                             'collection_case': 'ACollectionCase',
                             'reporting_unit': 'AReportingUnit',
                             'collection_instrument': 'ACollectionInstrument'}

        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    def test_post_request_all_message_fails(self):
        """sends POST request to the application messageList endpoint"""
        url = "http://localhost:5050/messages"
        response = self.app.post(url)
        self.assertEqual(response.status_code, 405)

    def test_that_checks_post_request_is_within_database(self):
        """check messages from messageSend endpoint saved in database correctly"""
        # check if json message is inside the database

        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}

        data = {'msg_to': 'richard',
                'msg_from': 'torrance',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'archived': False,
                'marked_as_read': False,
                'create_date': datetime.now(timezone.utc),
                'read_date': datetime.now(timezone.utc)}


        self.app.post(url, data=json.dumps(data), headers=headers)

        engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)

        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message WHERE id = (SELECT MAX(id) FROM secure_message)')
            for row in request:
                data = {"to": row['msg_to'], "from": row['msg_from'], "subject": row['subject'], "body": row['body']}
                self.assertEqual({'to': 'richard', 'from': 'torrance', 'subject': 'MyMessage', 'body': 'hello'}, data)

    def test_post_request_returns_201_on_success(self):
        """check messages from messageSend endpoint saved in database"""
        # post json message written up in the ui
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}

        response = self.app.post(url, data=json.dumps(self.test_message), headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_post_request_stores_uuid_in_msg_id_if_message_post_called_with_no_msg_id_set(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}
        self.test_message['msg_id'] = ''
        self.app.post(url, data=json.dumps(self.test_message), headers=headers)
        engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)
        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message WHERE id = (SELECT MAX(id) FROM secure_message)')

            for row in request:
                self.assertEqual(len(row['msg_id']), 36)

    def test_reply_to_existing_message_has_same_thread_id_and_different_messge_id_as_original(self):
        """check a reply gets same thread id as original"""
        # post json message written up in the ui

        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}
        self.test_message['msg_id'] = ''
        self.app.post(url, data=json.dumps(self.test_message), headers=headers)

        # Now read back the message to get the thread ID

        engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)
        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message WHERE id = (SELECT MAX(id) FROM secure_message)')
            for row in request:
                self.test_message['thread_id'] = row['thread_id']

        # Now submit a new message as a reply , Message Id empty , thread id same as last one
        self.test_message['msg_id'] = ''
        self.app.post(url, data=json.dumps(self.test_message), headers=headers)

        # Now read back the two messages
        original_msg_id = original_thread_id = reply_msg_id = reply_thread_id = ''
        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message ORDER BY id ASC')
            for row in request:
                if row[0] == 1:
                    original_msg_id = row['msg_id']
                    original_thread_id = row['thread_id']
                if row[0] == 2:
                    reply_msg_id = row['msg_id']
                    reply_thread_id = row['thread_id']

        self.assertTrue(len(original_msg_id) > 0)
        self.assertTrue(len(original_thread_id) > 0)
        self.assertTrue(len(reply_msg_id) > 0)
        self.assertTrue(len(reply_thread_id) > 0)
        self.assertFalse(original_msg_id == reply_msg_id)
        self.assertTrue(original_thread_id == reply_thread_id)
        self.assertTrue(len(original_thread_id) == 36)  # UUID length
        self.assertTrue(len(reply_msg_id) == 36)

    def test_missing_read_status_does_not_cause_exception(self):
        """posts to message send end point without 'read-status'"""
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}
        now = datetime.now(timezone.utc)
        test_message = {'msg_id': 'AMsgId',    # No read_Status
                        'msg_to': 'richard',
                        'msg_from': 'torrance',
                        'subject': 'MyMessage',
                        'body': 'hello',
                        'thread_id': "",
                        'archive_status': False,
                        'sent_date': now,
                        'read_date': now,
                        'collection_case': 'ACollectionCase',
                        'reporting_unit': 'AReportingUnit',
                        'collection_instrument': 'ACollectionInstrument'}
        try:
            self.app.post(url, data=json.dumps(test_message), headers=headers)
            self.assertTrue(True)  # i.e no exception
        except Exception as e:
            self.fail("post rasied unexpected exception: {0}".format(e))

    def test_missing_archive_status_does_not_cause_exception(self):
        """posts to message send end point without 'archive_status'"""
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}
        now = datetime.now(timezone.utc)
        test_message = {'msg_id': 'AMsgId',
                        'msg_to': 'richard',
                        'msg_from': 'torrance',
                        'subject': 'MyMessage',
                        'body': 'hello',
                        'thread_id': "",
                        'read_status': False,
                        'sent_date': now,
                        'read_date': now,
                        'collection_case': 'ACollectionCase',
                        'reporting_unit': 'AReportingUnit',
                        'collection_instrument': 'ACollectionInstrument'}
        try:
            self.app.post(url, data=json.dumps(test_message), headers=headers)
            self.assertTrue(True)  # i.e no exception
        except Exception as e:
            self.fail("post raised unexpected exception: {0}".format(e))

    def test_missing_thread_id_does_not_cause_exception(self):
        """posts to message send end point without 'thread_id'"""
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}
        now = datetime.now(timezone.utc)
        test_message = {'msg_id': 'AMsgId',
                        'msg_to': 'richard',
                        'msg_from': 'torrance',
                        'subject': 'MyMessage',
                        'body': 'hello',
                        'read_status': False,
                        'archive_status': False,
                        'sent_date': now,
                        'read_date': now,
                        'collection_case': 'ACollectionCase',
                        'reporting_unit': 'AReportingUnit',
                        'collection_instrument': 'ACollectionInstrument'}
        try:
            self.app.post(url, data=json.dumps(test_message), headers=headers)
            self.assertTrue(True)  # i.e no exception
        except Exception as e:
            self.fail("post raised unexpected exception: {0}".format(e))

    def test_message_post_missing_msg_to_returns_error_to_caller(self):
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}

        self.test_message['msg_to'] = ''

        response = self.app.post(url, data=json.dumps(self.test_message), headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('To field not populated' in response.data.decode("utf-8"))


if __name__ == '__main__':
    unittest.main()
