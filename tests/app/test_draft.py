import uuid
import unittest
from unittest import mock
from flask import g
from flask import current_app, json
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from werkzeug.exceptions import InternalServerError
from app import application, settings, constants
from app.application import app
from app.authentication.jwe import Encrypter
from app.authentication.jwt import encode
from app.common import utilities
from app.common.alerts import AlertUser, AlertViaGovNotify
from app.common.labels import Labels
from app.repository import database
from app.repository.retriever import Retriever
from app.repository.saver import Saver
from app.resources.drafts import DraftModifyById, DraftSave
from app.validation.domain import DraftSchema
from app.validation.user import User
from app.constants import MAX_RU_ID_LEN
from app.services.service_toggles import party, case_service


class DraftTestCase(unittest.TestCase):
    """Test case for draft saving"""

    def setUp(self):
        """setup test environment"""
        self.app = application.app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db')
        token_data = {
            constants.USER_IDENTIFIER: constants.BRES_USER,
            "role": "internal"
        }
        encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                              _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                              _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
        signed_jwt = encode(token_data)
        encrypted_jwt = encrypter.encrypt_token(signed_jwt)
        AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

        self.url = "http://localhost:5050/draft/save"

        self.headers = {'Content-Type': 'application/json', 'Authorization': encrypted_jwt}

        self.test_message = {'msg_to': ['f62dfda8-73b0-4e0e-97cf-1b06327a6712'],
                             'msg_from': constants.BRES_USER,
                             'subject': 'MyMessage',
                             'body': 'hello',
                             'thread_id': '',
                             'collection_case': 'ACollectionCase',
                             'collection_exercise': 'ACollectionExercise',
                             'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
                             'survey': constants.BRES_SURVEY}
        settings.NOTIFY_CASE_SERVICE = '1'

        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            self.db = database.db

        self.user_internal = User('ce12b958-2a5f-44f4-a6da-861e59070a31', 'internal')
        self.user_respondent = User('0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'respondent')
        case_service.use_mock_service()
        party.use_mock_service()

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """enable foreign key constraint for tests"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def test_draft_call_saver(self):
        """Test saver called as expected to save draft"""

        saver = mock.Mock(Saver())

        draft_save = DraftSave()
        with app.app_context():
            g.user = User(constants.BRES_USER, 'internal')
            draft = DraftSchema().load(self.test_message)
            draft_save._save_draft(draft, saver)

        saver.save_message.assert_called_with(draft.data)
        saver.save_msg_status.assert_called_with(draft.data.msg_from, draft.data.msg_id, Labels.DRAFT.value)

    def test_draft_empty_to_field_returns_201(self):
        """Test draft can be saved without To field"""

        self.test_message['msg_to'] = []
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

    def test_draft_empty_collection_exercise_field_returns_201(self):
        """Test draft can be saved without Collection Exercise field"""

        self.test_message['collection_exercise'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_ru_id_field_returns_201(self):
        """Test draft can be saved without Reporting Unit field"""

        self.test_message['ru_id'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_survey_field_returns_201(self):
        """Test draft can be saved without Survey field"""

        self.test_message['ru_id'] = ''
        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_empty_from_field_returns_400(self):
        """Test that From field is required"""

        self.test_message['msg_from'] = ''

        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_draft_empty_survey_field_returns_400(self):
        """Test survey field is required"""

        self.test_message['survey'] = ''

        response = self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_draft_correct_labels_saved_to_status_without_to(self):
        """Check correct labels are saved to status table for draft saved without a to"""

        self.test_message['msg_to'] = []

        self.app.post(self.url, data=json.dumps(self.test_message), headers=self.headers)

        with self.engine.connect() as con:
            request = con.execute("SELECT * FROM secure_message ORDER BY id DESC LIMIT 1")

            for row in request:
                self.msg_id = row['msg_id']

            label_request = con.execute("SELECT * FROM status")

            self.assertTrue(label_request is not None)

            for row in label_request:
                self.assertEqual(row['msg_id'], self.msg_id)
                self.assertEqual(row['actor'], self.test_message['survey'])
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
                self.assertTrue(row['actor'], self.test_message['msg_to'])
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

        self.test_message.update({'msg_id': self.msg_id,
                                  'msg_to': ['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'],
                                  'msg_from': constants.BRES_USER,
                                  'subject': 'MyMessage',
                                  'body': 'hello',
                                  'thread_id': '',
                                  'collection_case': 'ACollectionCase',
                                  'collection_exercise': 'ACollectionExercise',
                                  'ru_id': 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                                  'survey': constants.BRES_SURVEY})

        response = self.app.post('http://localhost:5050/message/send', data=json.dumps(self.test_message),
                                 headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_draft_modified_since_last_read_true(self):
        """Test draft_modified_since_last_read function returns true for valid draft id"""

        with self.engine.connect() as con:
            msg_id = str(uuid.uuid4())
            query = 'INSERT INTO secure_message(msg_id, subject, body, thread_id,' \
                    ' collection_case, ru_id, survey) VALUES ("{0}", "test","test","", ' \
                    ' "ACollectionCase", "f1a5e99c-8edf-489a-9c72-6cabe6c387fc", "ACollectionExercise"' \
                    '"BRES")'.format(msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT", "{0}", ' \
                    '"0a7ad740-10d5-4ecb-b7ca-3c0384afb882")'.format(msg_id)
            con.execute(query)
            query = 'INSERT INTO status(label, msg_id, actor) VALUES("DRAFT_INBOX", "{0}",' \
                    ' "SurveyType")'.format(msg_id)
            con.execute(query)

        with app.app_context():
            with current_app.test_request_context():
                is_valid_draft = Retriever().check_msg_id_is_a_draft(msg_id, self.user_respondent)
        self.assertTrue(is_valid_draft[0])

    def test_draft_modified_since_last_read_false(self):
        """Test draft_modified_since_last_read function returns false for valid draft id"""

        with app.app_context():
            with current_app.test_request_context():
                is_valid_draft = Retriever().check_msg_id_is_a_draft('000000-0000-00000', self.user_respondent)
        self.assertFalse(is_valid_draft[0])

    def test_etag_check_returns_true_if_data_equal(self):
        """Test etag_check function returns true for unchanged draft etag"""

        message = {'msg_to': [constants.BRES_USER],
                   'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                   'msg_id': 'ea420f66-12f6-4d4e-bf36-fe9b6b20c3f4',
                   'subject': 'test',
                   'body': 'test',
                   'thread_id': '',
                   'collection_case': 'ACollectionCase',
                   'collection_exercise': 'ACollectionExercise',
                   'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
                   'survey': constants.BRES_SURVEY,
                   '_links': '',
                   'labels': ['DRAFT']}

        etag = utilities.generate_etag(message['msg_to'], message['msg_id'], message['subject'], message['body'])

        self.assertTrue(DraftModifyById.etag_check({'etag': etag}, message))

    def test_etag_check_returns_false_if_msg_to_changed(self):
        """Test etag_check function returns false for changed draft etag"""

        message = {'msg_to': [constants.BRES_USER],
                   'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                   'msg_id': 'ea420f66-12f6-4d4e-bf36-fe9b6b20c3f4',
                   'subject': 'test',
                   'body': 'test',
                   'thread_id': '',
                   'collection_case': 'ACollectionCase',
                   'collection_exercise': 'ACollectionExercise',
                   'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
                   'survey': constants.BRES_SURVEY,
                   '_links': '',
                   'labels': ['DRAFT']}

        etag = utilities.generate_etag(['XXX'], message['msg_id'], message['subject'], message['body'])
        self.assertFalse(DraftModifyById.etag_check({'ETag': etag}, message))

    def test_etag_check_returns_false_if_msg_id_changed(self):
        """Test etag_check function returns false for changed draft etag"""

        message = {'msg_to': [constants.BRES_USER],
                   'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                   'msg_id': 'ea420f66-12f6-4d4e-bf36-fe9b6b20c3f4',
                   'subject': 'test',
                   'body': 'test',
                   'thread_id': '',
                   'collection_case': 'ACollectionCase',
                   'collection_exercise': 'ACollectionExercise',
                   'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
                   'survey': constants.BRES_SURVEY,
                   '_links': '',
                   'labels': ['DRAFT']}

        etag = utilities.generate_etag(message['msg_to'], 'XXX', message['subject'], message['body'])
        self.assertFalse(DraftModifyById.etag_check({'ETag': etag}, message))

    def test_etag_check_returns_false_if_subject_changed(self):
        """Test etag_check function returns false for changed draft etag"""

        message = {'msg_to': [constants.BRES_USER],
                   'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                   'msg_id': 'ea420f66-12f6-4d4e-bf36-fe9b6b20c3f4',
                   'subject': 'test',
                   'body': 'test',
                   'thread_id': '',
                   'collection_case': 'ACollectionCase',
                   'collection_exercise': 'ACollectionExercise',
                   'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
                   'survey': constants.BRES_SURVEY,
                   '_links': '',
                   'labels': ['DRAFT']}

        etag = utilities.generate_etag(message['msg_to'], message['msg_id'], 'XXX', message['body'])
        self.assertFalse(DraftModifyById.etag_check({'ETag': etag}, message))

    def test_etag_check_returns_false_if_body_changed(self):
        """Test etag_check function returns false for changed draft etag"""

        message = {'msg_to': [constants.BRES_USER],
                   'msg_from': '0a7ad740-10d5-4ecb-b7ca-3c0384afb882',
                   'msg_id': 'ea420f66-12f6-4d4e-bf36-fe9b6b20c3f4',
                   'subject': 'test',
                   'body': 'test',
                   'thread_id': '',
                   'collection_case': 'ACollectionCase',
                   'collection_exercise': 'ACollectionExercise',
                   'ru_id': '7fc0e8ab-189c-4794-b8f4-9f05a1db185b',
                   'survey': constants.BRES_SURVEY,
                   '_links': '',
                   'labels': ['DRAFT']}

        etag = utilities.generate_etag(message['msg_to'], message['msg_id'], message['subject'], 'XXX')
        self.assertFalse(DraftModifyById.etag_check({'ETag': etag}, message))

    def test_draft_modified_since_last_read_t_raises_error(self):
        """Test draft_modified_since_last_read function raises internal server error"""
        msg_id = str(uuid.uuid4())
        with app.app_context():
            database.db.drop_all()
            with current_app.test_request_context():
                with self.assertRaises(InternalServerError):
                    Retriever().check_msg_id_is_a_draft(msg_id, self.user_respondent)

    def test_draft_same_to_from_causes_error(self):
        """marshalling message with same to and from field"""
        # self.test_message['msg_to'] = self.test_message['msg_from']
        if self.test_message['msg_from'] in self.test_message['msg_to']:
            with app.app_context():
                g.user = User(self.test_message['msg_from'], 'respondent')
                schema = DraftSchema()
                errors = schema.load(self.test_message)[1]

            self.assertTrue(errors == {'_schema': ['msg_to and msg_from fields can not be the same.']})

    def test_draft_msg_to_list_of_string(self):
        """marshalling message where msg_to field is list of strings"""
        self.test_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with app.app_context():
            g.user = User(self.test_message['msg_from'], 'respondent')
            schema = DraftSchema()
            errors = schema.load(self.test_message)[1]

        self.assertTrue(errors == {})

    def test_draft_msg_to_string(self):
        """marshalling message where msg_to field is string"""
        self.test_message['msg_to'] = ["01b51fcc-ed43-4cdb-ad1c-450f9986859b"]
        with app.app_context():
            g.user = User(self.test_message['msg_from'], 'respondent')
            schema = DraftSchema()
            errors = schema.load(self.test_message)[1]

        self.assertTrue(errors == {})

    def test_draft_msg_from_string(self):
        """marshalling message where msg_from field is string"""
        self.test_message['msg_from'] = "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
        with app.app_context():
            g.user = User(self.test_message['msg_from'], 'respondent')
            schema = DraftSchema()
            errors = schema.load(self.test_message)[1]

        self.assertTrue(errors == {})

    def test_ru_id_field_too_long_causes_error(self):
        """marshalling message with ru_id field too long"""
        self.test_message['ru_id'] = "x" * (MAX_RU_ID_LEN + 1)
        expected_error = 'ru_id field length must not be greater than {0}.'.format(MAX_RU_ID_LEN)
        with app.app_context():
            g.user = User(self.test_message['msg_from'], 'respondent')
            schema = DraftSchema()
            sut = schema.load(self.test_message)
        self.assertTrue(expected_error in sut.errors['ru_id'])
