import unittest
from datetime import datetime, timezone
from unittest import mock
from flask import current_app
from flask import json
from sqlalchemy import create_engine
from app import application
from app import settings
from app.application import app
from app.common.alerts import AlertUser, AlertViaGovNotify
from app.repository import database
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter


class FlaskTestCase(unittest.TestCase):
    """Test case for application endpoints"""

    def setUp(self):
        """setup test environment"""
        self.app = application.app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db', echo=True)

        AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

        token_data = {
            "user_urn": "12345678910"
        }
        encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                              _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                              _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
        signed_jwt = encode(token_data)
        encrypted_jwt = encrypter.encrypt_token(signed_jwt)
        AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

        self.url = "http://localhost:5050/draft/save"

        self.headers = {'Content-Type': 'application/json', 'authentication': encrypted_jwt}

        self.test_message = {'urn_to': 'richard',
                             'urn_from': 'torrance',
                             'subject': 'MyMessage',
                             'body': 'hello',
                             'thread_id': "",
                             'collection_case': 'ACollectionCase',
                             'reporting_unit': 'AReportingUnit',
                             'survey': 'test-123'}

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

        data = {'urn_to': 'richard',
                'urn_from': 'torrance',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'create_date': datetime.now(timezone.utc),
                'read_date': datetime.now(timezone.utc)}

        self.app.post(url, data=json.dumps(data), headers=self.headers)

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message WHERE id = (SELECT MAX(id) FROM secure_message)')
            for row in request:
                data = {"subject": row['subject'], "body": row['body']}
                self.assertEqual({'subject': 'MyMessage', 'body': 'hello'}, data)

    def test_message_post_request_returns_201_and_msg_id(self):
        """check messages from messageSend endpoint saved in database"""
        # post json message written up in the ui
        url = "http://localhost:5050/message/send"

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        msg_resp = json.loads(response.data)
        msg_id = msg_resp['msg_id']
        self.assertTrue(msg_id is not None)
        self.assertEqual(response.status_code, 201)

    def test_post_request_with_msg_id_returns_bad_request(self):
        """Check message sent with msg_id returns bad request"""

        url = "http://localhost:5050/message/send"

        data = {'msg_id': '',
                'urn_to': 'richard',
                'urn_from': 'torrance',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'create_date': datetime.now(timezone.utc),
                'read_date': datetime.now(timezone.utc)}

        response = self.app.post(url, data=json.dumps(data), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_post_request_stores_uuid_in_msg_id_if_message_post_called_with_no_msg_id_set(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/message/send"

        self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)
        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message WHERE id = (SELECT MAX(id) FROM secure_message)')

            for row in request:
                self.assertEqual(len(row['msg_id']), 36)

    def test_reply_to_existing_message_has_same_thread_id_and_different_messge_id_as_original(self):
        """check a reply gets same thread id as original"""
        # post json message written up in the ui

        url = "http://localhost:5050/message/send"

        self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)

        # Now read back the message to get the thread ID

        engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)
        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message WHERE id = (SELECT MAX(id) FROM secure_message)')
            for row in request:
                self.test_message['thread_id'] = row['thread_id']

        # Now submit a new message as a reply , Message Id empty , thread id same as last one
        self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)

        # Now read back the two messages
        original_msg_id = original_thread_id = reply_msg_id = reply_thread_id = ''
        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message ORDER BY id DESC')
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

    def test_missing_thread_id_does_not_cause_exception(self):
        """posts to message send end point without 'thread_id'"""
        url = "http://localhost:5050/message/send"

        now = datetime.now(timezone.utc)
        test_message = {'urn_to': 'richard',
                        'urn_from': 'torrance',
                        'subject': 'MyMessage',
                        'body': 'hello',
                        'sent_date': now,
                        'read_date': now,
                        'collection_case': 'ACollectionCase',
                        'reporting_unit': 'AReportingUnit',
                        'survey': 'ACollectionInstrument'}
        try:
            self.app.post(url, data=json.dumps(test_message), headers=self.headers)
            self.assertTrue(True)  # i.e no exception
        except Exception as e:
            self.fail("post raised unexpected exception: {0}".format(e))

    def test_message_post_missing_msg_to_returns_error_to_caller(self):
        """posts to message send end point without 'urn_to'"""
        url = "http://localhost:5050/message/send"

        self.test_message['urn_to'] = ''

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_message_post_missing_urn_from_returns_error(self):
        """posts to message send end point without 'urn_from'"""
        url = "http://localhost:5050/message/send"

        self.test_message['urn_from'] = ''

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_message_post_too_large_urn_from_returns_error(self):
        """posts to message send end point with too large 'urn_from'"""
        url = "http://localhost:5050/message/send"

        self.test_message['urn_from'] = 'x' * 101

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_message_post_too_large_urn_to_returns_error(self):
        """posts to message send end point with too large 'urn_from'"""
        url = "http://localhost:5050/message/send"

        self.test_message['urn_to'] = 'x' * 101

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_message_post_stores_labels_correctly_for_sender_of_message(self):
        """posts to message send end point to ensure labels are saved as expected"""
        url = "http://localhost:5050/message/send"

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM status WHERE label='SENT' AND msg_id='{0}' AND actor='{1}'"
                                  .format(data['msg_id'], self.test_message['survey']))
            for row in request:
                self.assertTrue(row is not None)

    def test_message_post_stores_labels_correctly_for_recipient_of_message(self):
        """posts to message send end point to ensure labels are saved as expected"""
        url = "http://localhost:5050/message/send"

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM status WHERE label='INBOX' OR label='UNREAD' AND msg_id='{0}'"
                                  " AND actor='{1}'".format(data['msg_id'], self.test_message['urn_to']))
            for row in request:
                self.assertTrue(row is not None)

    def test_message_post_stores_status_correctly_for_internal_user(self):
        """posts to message send end point to ensure survey is saved for internal user"""
        url = "http://localhost:5050/message/send"

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM status WHERE msg_id='{0}' AND actor='{1}' AND label='SENT'"
                                  .format(data['msg_id'], self.test_message['survey']))
            for row in request:
                self.assertTrue(row is not None)

    def test_message_post_stores_audit_correctly_for_internal_user(self):
        """Test internal user details have been added to audit table on send message"""

        url = "http://localhost:5050/message/send"

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM internal_sent_audit WHERE msg_id='{0}' AND internal_user='{1}'"
                                  .format(data['msg_id'], self.test_message['urn_from']))

            for row in request:
                self.assertTrue(row is not None)

    def test_draft_post_returns_201_and_msg_id(self):
        """Check send draft successful"""
        url = "http://localhost:5050/draft/save"

        response = self.app.post(url, data=json.dumps(self.test_message), headers=self.headers)
        msg_resp = json.loads(response.data)
        msg_id = msg_resp['msg_id']
        self.assertTrue(msg_id is not None)
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
