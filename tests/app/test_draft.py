from app.resources.drafts import Drafts
import unittest
from app.repository.saver import Saver
from unittest import mock
from app.validation.domain import DraftSchema
from app.validation.labels import Labels
from app import application
from sqlalchemy import create_engine
from app.common.alerts import AlertUser, AlertViaGovNotify
from app.repository import database
from flask import current_app, json
from app.application import app


class DraftTestCase(unittest.TestCase):
    """Test case for draft saving"""

    def setUp(self):
        """setup test environment"""
        self.app = application.app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        self.engine = create_engine('sqlite:////tmp/messages.db', echo=True)

        AlertUser.alert_method = mock.Mock(AlertViaGovNotify)

        self.url = "http://localhost:5050/draft/save"

        self.headers = {'Content-Type': 'application/json', 'user_urn': ''}

        self.test_message = {'urn_to': 'richard',
                             'urn_from': 'torrance',
                             'subject': 'MyMessage',
                             'body': 'hello',
                             'sent_date': None,
                             'read_date': None,
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

        Drafts.save_draft(draft, saver)

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
