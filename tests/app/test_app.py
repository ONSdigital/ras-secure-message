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
from app.resources.messages import MessageSend
from app.common.alerts import AlertViaGovNotify


class FlaskTestCase(unittest.TestCase):
    """Test case for application endpoints"""
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

        MessageSend.alert_method = mock.PropertyMock(return_value=mock.Mock(AlertViaGovNotify))

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
                # print("to:", row['msg_to'], "from:", row['msg_from'], "body:", row['body'])
                self.assertEqual({'to': 'richard', 'from': 'torrance', 'subject': 'MyMessage', 'body': 'hello'}, data)

    def test_post_request_returns_201_on_success(self):
        """check messages from messageSend endpoint saved in database"""
        # post json message written up in the ui
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}
        data = {'msg_to': 'richard',
                'msg_from': 'torrance',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'archived': False,
                'marked_as_read': False,
                'create_date': datetime.now(timezone.utc)}

        response = self.app.post(url, data=json.dumps(data), headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_post_request_stores_uuid_if_message_post_called(self):
        """check default_msg_id is stored when messageSend endpoint called with no msg_id"""
        # post json message written up in the ui
        url = "http://localhost:5050/message/send"
        headers = {'Content-Type': 'application/json'}
        data = {'msg_to': 'richard',
                'msg_from': 'torrance',
                'subject': 'MyMessage',
                'body': 'hello',
                'thread': "?",
                'archived': False,
                'marked_as_read': False,
                'create_date': datetime.now(timezone.utc)}

        self.app.post(url, data=json.dumps(data), headers=headers)
        engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)
        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message WHERE id = (SELECT MAX(id) FROM secure_message)')

            for row in request:
                self.assertEqual(len(row['msg_id']), 36)



if __name__ == '__main__':
    unittest.main()
