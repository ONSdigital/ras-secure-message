import hashlib
import unittest
import uuid
from app.repository.retriever import Retriever
from unittest import mock
from flask import current_app, json
from sqlalchemy import create_engine
from werkzeug.exceptions import InternalServerError
from app import application
from app import settings
from app.application import app
from app.authentication.jwe import Encrypter
from app.authentication.jwt import encode
from app.common.alerts import AlertUser, AlertViaGovNotify
from app.common.labels import Labels
from app.repository import database
from app.repository.saver import Saver
from app.resources.drafts import DraftModifyById
from app.resources.drafts import DraftSave
from app.validation.domain import DraftSchema


class DraftTestCase(unittest.TestCase):
    """Test case for draft saving"""

    def setUp(self):
        """setup test environment"""
        self.app = application.app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')
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

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_jwt}

        self.test_message = {'urn_to': 'richard',
                             'urn_from': 'torrance',
                             'subject': 'MyMessage',
                             'body': 'hello',
                             'thread_id': '',
                             'collection_case': 'ACollectionCase',
                             'reporting_unit': 'AReportingUnit',
                             'survey': 'ACollectionInstrument'}

        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

    def test_draft_call_saver(self):
        """Test saver called as expected to save draft"""

        saver = mock.Mock(Saver())

        draft = DraftSchema().load(self.test_message)

        draft_save = DraftSave()

        draft_save._save_draft(draft, saver)

        saver.save_message.assert_called_with(draft.data)
        saver.save_msg_status.assert_called_with(draft.data.urn_from, draft.data.msg_id, Labels.DRAFT.value)

    def test_draft_empty_to_field_returns_201(self):
        """Test draft can be saved without To field"""

        self.test_message['urn_to'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_subject_field_returns_201(self):
        """Test draft can be saved without Subject field"""

        self.test_message['subject'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_body_field_returns_201(self):
        """Test draft can be saved without Body field"""

        self.test_message['body'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_collection_case_field_returns_201(self):
        """Test draft can be saved without Collection Case field"""

        self.test_message['collection_case'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_reporting_unit_field_returns_201(self):
        """Test draft can be saved without Reporting Unit field"""

        self.test_message['reporting_unit'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_survey_field_returns_201(self):
        """Test draft can be saved without Survey field"""

        self.test_message['reporting_unit'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_from_field_returns_400(self):
        """Test that From field is required"""

        self.test_message['urn_from'] = ''

        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_draft_empty_survey_field_returns_400(self):
        """Test survey field is required"""

        self.test_message['survey'] = ''

        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_draft_correct_labels_saved_to_status_without_to(self):
        """Check correct labels are saved to status table for draft saved without a to"""

        self.test_message['urn_to'] = ''

        self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM secure_message ORDER BY id DESC LIMIT 1")

            for row in request:
                self.msg_id = row['msg_id']

            label_request = con.execute("SELECT * FROM status")

            self.assertTrue(label_request is not None)

            for row in label_request:
                self.assertEqual(row['msg_id'], self.msg_id)
                self.assertEqual(row['actor'], self.test_message['urn_from'])
                self.assertEqual(row['label'], Labels.DRAFT.value)

    def test_draft_correct_labels_saved_to_status_with_to(self):
        """Check correct labels are saved to status table for draft saved without a to"""

        self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM secure_message ORDER BY id DESC LIMIT 1")

            for row in request:
                self.msg_id = row['msg_id']

            label_request = con.execute("SELECT * FROM status")

            self.assertTrue(label_request is not None)

            for row in label_request:
                self.assertTrue(row['msg_id'], self.msg_id)
                self.assertTrue(row['actor'], self.test_message['urn_to'])
                self.assertTrue(row['label'], Labels.DRAFT_INBOX.value)

    def test_draft_inserted_into_msg_table(self):
        """Check draft has been added to SecureMessage table"""

        self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM secure_message LIMIT 1")
            self.assertTrue(request is not None)

    def test_draft_sent_successfully_return_201(self):
        """Send message that is a draft"""

        self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM secure_message LIMIT 1")
            for row in request:
                self.msg_id = row['msg_id']

        self.test_message.update(
            {
                'msg_id': self.msg_id,
                'urn_to': 'richard',
                'urn_from': 'torrance',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread_id': '',
                'collection_case': 'ACollectionCase',
                'reporting_unit': 'AReportingUnit',
                'survey': 'ACollectionInstrument'
            }
        )

        response = self.app.post('http://localhost:5050/message/send', data=json.dumps(self.test_message),
                                 headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_modified_since_last_read_true(self):
        """Test draft_modified_since_last_read function returns true for valid draft id"""

        with self.engine.connect() as con:
            msg_id = str(uuid.uuid4())
            query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                    ' collection_case, reporting_unit, survey) VALUES ("{0}", "test","test","", ' \
                    ' "ACollectionCase", "AReportingUnit", ' \
                    '"SurveyType")'.format(msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT", "{0}", "respondent.21345")'.format(
                msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT_INBOX", "{0}",' \
                    ' "SurveyType")'.format(msg_id)
            con.execute(query)

        with app.app_context():
            with current_app.test_request_context():
                is_valid_draft = Retriever().check_msg_id_is_a_draft(msg_id, 'respondent.21345')
        self.assertTrue(is_valid_draft[0])

    def test_draft_modified_since_last_read_false(self):
        """Test draft_modified_since_last_read function returns false for valid draft id"""

        with app.app_context():
            with current_app.test_request_context():
                is_valid_draft = Retriever().check_msg_id_is_a_draft('000000-0000-00000', 'respondent.21345')
        self.assertFalse(is_valid_draft[0])

    def test_etag_check_returns_true(self):
        """Test etag_check function returns true for unchanged draft etag"""

        with self.engine.connect() as con:
            msg_id = str(uuid.uuid4())
            query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                    ' collection_case, reporting_unit, survey) VALUES ("{0}", "test","test","", ' \
                    ' "ACollectionCase", "AReportingUnit", ' \
                    '"SurveyType")'.format(msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT", "{0}", "respondent.21345")'.format(
                msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT_INBOX", "{0}",' \
                    ' "SurveyType")'.format(msg_id)
            con.execute(query)

        with app.app_context():
            with current_app.test_request_context():
                is_valid_draft = Retriever().check_msg_id_is_a_draft(msg_id, 'respondent.21345')
        hash_object = hashlib.sha1(str(sorted(is_valid_draft[1].items())).encode())
        etag = hash_object.hexdigest()

        self.assertTrue(DraftModifyById.etag_check({'etag': etag}, is_valid_draft[1]))

    def test_etag_check_returns_false(self):
        """Test etag_check function returns false for changed draft etag"""

        with self.engine.connect() as con:
            msg_id = str(uuid.uuid4())
            query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                    ' collection_case, reporting_unit, survey) VALUES ("{0}", "test","test","", ' \
                    ' "ACollectionCase", "AReportingUnit", ' \
                    '"SurveyType")'.format(msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT", "{0}", "respondent.21345")'.format(
                msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT_INBOX", "{0}",' \
                    ' "SurveyType")'.format(msg_id)
            con.execute(query)

        with app.app_context():
            with current_app.test_request_context():
                is_valid_draft = Retriever().check_msg_id_is_a_draft(msg_id, 'respondent.21345')

        etag = '1234567sdfghj98765fgh'

        self.assertFalse(DraftModifyById.etag_check({'etag': etag}, is_valid_draft[1]))

    def test_draft_modified_since_last_read_t_raises_error(self):
        """Test draft_modified_since_last_read function raises internal server error"""
        msg_id = str(uuid.uuid4())
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().check_msg_id_is_a_draft(msg_id, 'respondent.21345')
