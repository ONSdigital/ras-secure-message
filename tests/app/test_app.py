import unittest
from unittest import mock
from unittest.mock import patch
from datetime import datetime, timezone
import uuid

from flask import current_app, json
from sqlalchemy import create_engine

from secure_message import application, constants
from secure_message.common.alerts import AlertUser, AlertViaGovNotify
from secure_message.repository import database
from secure_message.authentication.jwt import encode
from secure_message.services.service_toggles import case_service, party, internal_user_service
from secure_message.resources.messages import MessageSend
from secure_message.resources.messages import logger as message_logger
from secure_message.common.alerts import AlertViaLogging
from secure_message.api_mocks.party_service_mock import PartyServiceMock
from secure_message.api_mocks.case_service_mock import CaseServiceMock
from secure_message.api_mocks.internal_user_service_mock import InternalUserServiceMock


class FlaskTestCase(unittest.TestCase):
    """Test case for application endpoints"""

    BRES_SURVEY = "33333333-22222-3333-4444-88dc018a1a4c"

    def setUp(self):
        """setup test environment"""
        self.app = application.create_app()
        self.client = self.app.test_client()
        self.engine = create_engine(self.app.config['SQLALCHEMY_DATABASE_URI'])

        AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

        internal_token_data = {constants.USER_IDENTIFIER: constants.NON_SPECIFIC_INTERNAL_USER,
                               "role": "internal"}

        external_token_data = {constants.USER_IDENTIFIER: str(uuid.uuid4()),
                               "role": "respondent"}

        with self.app.app_context():
            internal_signed_jwt = encode(internal_token_data)
            external_signed_jwt = encode(external_token_data)

        AlertUser.alert_method = mock.Mock(AlertViaLogging)
        self.app.config['NOTIFY_CASE_SERVICE'] = '1'

        self.internal_user_header = {'Content-Type': 'application/json', 'Authorization': internal_signed_jwt}
        self.external_user_header = {'Content-Type': 'application/json', 'Authorization': external_signed_jwt}

        self.test_message = {'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                             'msg_from': constants.NON_SPECIFIC_INTERNAL_USER,
                             'subject': 'MyMessage',
                             'body': 'hello',
                             'thread_id': "",
                             'collection_case': 'ACollectionCase',
                             'collection_exercise': 'ACollectionExercise',
                             'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                             'survey': self.BRES_SURVEY}

        with self.app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        party.use_mock_service()
        case_service.use_mock_service()
        internal_user_service.use_mock_service()

    def test_that_checks_post_request_is_within_database(self):
        """check messages from messageSend endpoint saved in database correctly"""
        # check if json message is inside the database

        url = "http://localhost:5050/message/send"

        data = {'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                'msg_from': 'ce12b958-2a5f-44f4-a6da-861e59070a31',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                'create_date': datetime.now(timezone.utc),
                'read_date': datetime.now(timezone.utc)}

        self.client.post(url, data=json.dumps(data), headers=self.internal_user_header)

        with self.engine.connect() as con:
            request = con.execute('SELECT * FROM securemessage.secure_message WHERE id = (SELECT MAX(id) FROM securemessage.secure_message)')
            for row in request:
                data = {"subject": row['subject'], "body": row['body']}
                self.assertEqual({'subject': 'MyMessage', 'body': 'hello'}, data)

    def test_post_request_stores_uuid_in_msg_id_if_message_post_called_with_no_msg_id_set(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/message/send"

        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        engine = create_engine(self.app.config['SECURE_MESSAGING_DATABASE_URL'], echo=True)
        with engine.connect() as con:
            request = con.execute('SELECT * FROM securemessage.secure_message WHERE id = (SELECT MAX(id) FROM securemessage.secure_message)')

            for row in request:
                self.assertEqual(len(row['msg_id']), 36)

    def test_thread_patch_without_content_type_in_header_fails(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/v2/threads/f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        header_copy = self.internal_user_header.copy()
        header_copy.pop('Content-Type')
        response = self.client.patch(url, data=json.dumps({"is_closed": True}), headers=header_copy)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.get_data()), {'message': 'Request must set accept content type "application/json" in header.'})

    def test_thread_patch_as_external_user_fails(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/v2/threads/f1a5e99c-8edf-489a-9c72-6cabe6c387fc"
        response = self.client.patch(url, data=json.dumps({"is_closed": True}), headers=self.external_user_header)
        self.assertEqual(response.status_code, 403)
        error_message = "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server."
        self.assertEqual(json.loads(response.get_data()), {'message': error_message})

    def test_reply_to_existing_message_has_same_thread_id_and_different_message_id_as_original(self):
        """check a reply gets same thread id as original"""
        # post json message written up in the ui

        url = "http://localhost:5050/message/send"

        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)

        # Now read back the message to get the thread ID

        engine = create_engine(self.app.config['SECURE_MESSAGING_DATABASE_URL'], echo=True)
        with engine.connect() as con:
            request = con.execute('SELECT * FROM securemessage.secure_message WHERE id = (SELECT MAX(id) FROM securemessage.secure_message)')
            for row in request:
                self.test_message['thread_id'] = row['thread_id']

        # Now submit a new message as a reply , Message Id empty , thread id same as last one
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)

        # Now read back the two messages
        original_msg_id = original_thread_id = reply_msg_id = reply_thread_id = ''
        with engine.connect() as con:
            request = con.execute('SELECT * FROM securemessage.secure_message ORDER BY id DESC')
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

        test_message = {'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                        'msg_from': 'ce12b958-2a5f-44f4-a6da-861e59070a31',
                        'subject': 'MyMessage',
                        'body': 'hello',
                        'collection_case': 'ACollectionCase',
                        'collection_exercise': 'ACollectionExercise',
                        'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                        'survey': self.BRES_SURVEY}
        try:
            self.client.post(url, data=json.dumps(test_message), headers=self.internal_user_header)
            self.assertTrue(True)  # i.e no exception
        except Exception as e:
            self.fail(f"post raised unexpected exception: {e}")

    def test_message_post_stores_labels_correctly_for_sender_of_message(self):
        """posts to message send end point to ensure labels are saved as expected"""
        url = "http://localhost:5050/message/send"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM securemessage.status WHERE label='SENT' AND msg_id='{0}' AND actor='{1}'"
                                  .format(data['msg_id'], self.test_message['survey']))
            for row in request:
                self.assertTrue(row is not None)

    def test_message_post_stores_events_correctly_for_message(self):
        """posts to message send end point to ensure events are saved as expected"""
        url = "http://localhost:5050/message/send"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            request = con.execute(f"SELECT * FROM securemessage.events WHERE event='Sent' AND msg_id='{data['msg_id']}'")
            for row in request:
                self.assertTrue(row is not None)

    def test_message_post_stores_labels_correctly_for_recipient_of_message(self):
        """posts to message send end point to ensure labels are saved as expected"""
        url = "http://localhost:5050/message/send"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)
        # dereferencing msg_to for purpose of test
        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM securemessage.status WHERE "
                                  "label='INBOX' OR label='UNREAD' AND msg_id='{0}'"
                                  " AND actor='{1}'".format(data['msg_id'], self.test_message['msg_to'][0]))
            for row in request:
                self.assertTrue(row is not None)

    def test_message_post_stores_status_correctly_for_internal_user(self):
        """posts to message send end point to ensure survey is saved for internal user"""
        url = "http://localhost:5050/message/send"

        response = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        data = json.loads(response.data)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM securemessage.status WHERE "
                                  "msg_id='{0}' AND actor='{1}' AND label='SENT'"
                                  .format(data['msg_id'], self.test_message['survey']))
            for row in request:
                self.assertTrue(row is not None)

    @patch.object(case_service, 'store_case_event')
    def test_case_service_not_called_on_sent_if_NotifyCaseService_is_not_set(self, case):
        """Test case service not called if not set to do so in config"""

        self.app.config['NOTIFY_CASE_SERVICE'] = '0'
        url = "http://localhost:5050/message/send"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(case.called)

    @patch.object(case_service, 'store_case_event')
    def test_case_service_called_on_sent_if_NotifyCaseService_is_set(self, case):
        """Test case service called if set to do so in config """

        self.app.config["NOTIFY_VIA_GOV_NOTIFY"] = '0'
        self.app.config['NOTIFY_CASE_SERVICE'] = '1'
        url = "http://localhost:5050/message/send"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertTrue(case.called)

    @patch.object(message_logger, 'error')
    @patch.object(MessageSend, '_try_send_alert_email', side_effect=Exception('SomethingBad'))
    def test_exception_in_alert_listeners_raises_exception_but_returns_201(self, mock_sender, mock_logger):
        """Test exceptions in alerting do not prevent a response indicating success"""
        self.app.config['NOTIFY_CASE_SERVICE'] = '0'
        url = "http://localhost:5050/message/send"
        result = self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertTrue(mock_logger.called)
        self.assertTrue(result.status_code == 201)

    @patch.object(PartyServiceMock, 'get_user_details', return_value=({"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                                                                       "firstName": "Bhavana",
                                                                       "lastName": "Lincoln",
                                                                       "telephone": "+443069990888",
                                                                       "status": "ACTIVE",
                                                                       "sampleUnitType": "BI"}, 200))
    @patch.object(AlertViaLogging, 'send')
    def test_if_user_has_no_email_address_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is missing no attempt will be made to send email """

        url = "http://localhost:5050/message/send"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)

    @patch.object(PartyServiceMock, 'get_user_details', return_value=({"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                                                                       "firstName": "Bhavana",
                                                                       "emailAddress": "",
                                                                       "lastName": "Lincoln",
                                                                       "telephone": "+443069990888",
                                                                       "status": "ACTIVE",
                                                                       "sampleUnitType": "BI"}, 200))
    @patch.object(AlertViaLogging, 'send')
    def test_if_user_has_zero_length_email_address_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is zero length no attempt will be made to send email """

        url = "http://localhost:5050/message/send"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)

    @patch.object(PartyServiceMock, 'get_user_details', return_value=({"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                                                                       "firstName": "Bhavana",
                                                                       "emailAddress": "   ",
                                                                       "lastName": "Lincoln",
                                                                       "telephone": "+443069990888",
                                                                       "status": "ACTIVE",
                                                                       "sampleUnitType": "BI"}, 200))
    @patch.object(AlertViaLogging, 'send')
    def test_if_user_has_only_whitespace_in_email_address_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is zero length no attempt will be made to send email """

        url = "http://localhost:5050/message/send"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)

    @patch.object(PartyServiceMock, 'get_user_details', return_value=({"id": "cantFindThis"}, 400))
    @patch.object(AlertViaLogging, 'send')
    def test_if_user_unknown_in_party_service_no_email_sent(self, mock_alerter, mock_party):
        """Test if Email Address is zero length no attempt will be made to send email """

        url = "http://localhost:5050/message/send"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        self.assertFalse(mock_alerter.called)

    @patch.object(PartyServiceMock, 'get_user_details', return_value=({"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                                                                       "emailAddress": "   ",
                                                                       "lastName": "",
                                                                       "telephone": "+443069990888",
                                                                       "status": "ACTIVE",
                                                                       "sampleUnitType": "BI"}))
    @patch.object(CaseServiceMock, 'store_case_event')
    def test_if_respondent_has_no_first_name_or_last_name_then_unknown_user_passed_to_case_service(self, mock_case, mock_party):
        """Test if party data has no name for the user then a constant of 'Unknown user' is used"""
        self.test_message.update({'msg_to': [constants.NON_SPECIFIC_INTERNAL_USER],
                                  'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                                  'subject': 'MyMessage',
                                  'body': 'hello',
                                  'collection_case': 'ACollectionCase',
                                  'collection_exercise': 'ACollectionExercise',
                                  'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                  'survey': self.BRES_SURVEY})

        token_data = {constants.USER_IDENTIFIER: "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
                      "role": "respondent"}

        with self.app.app_context():
            signed_jwt = encode(token_data)

        self.internal_user_header = {'Content-Type': 'application/json', 'Authorization': signed_jwt}
        url = "http://localhost:5050/message/send"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        mock_case.assert_called()

    @patch.object(InternalUserServiceMock, 'get_user_details', return_value=({"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                                                                              "emailAddress": "   ",
                                                                              "lastName": "",
                                                                              "telephone": "+443069990888"}))
    @patch.object(CaseServiceMock, 'store_case_event')
    def test_if_internal_user_has_no_first_name_or_last_name_then_unknown_user_passed_to_case_service(self, mock_case, mock_party):
        """Test if party data has no name for the user then a constant of 'Unknown user' is used"""
        self.test_message.update({'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                                  'msg_from': 'f62dfda8-73b0-4e0e-97cf-1b06327a6712',
                                  'subject': 'MyMessage',
                                  'body': 'hello',
                                  'collection_case': 'ACollectionCase',
                                  'collection_exercise': 'ACollectionExercise',
                                  'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                  'survey': self.BRES_SURVEY})

        token_data = {constants.USER_IDENTIFIER: "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                      "role": "internal"}

        with self.app.app_context():
            signed_jwt = encode(token_data)

        self.internal_user_header = {'Content-Type': 'application/json', 'Authorization': signed_jwt}
        url = "http://localhost:5050/v2/messages"
        self.client.post(url, data=json.dumps(self.test_message), headers=self.internal_user_header)
        mock_case.assert_called()


if __name__ == '__main__':
    unittest.main()
