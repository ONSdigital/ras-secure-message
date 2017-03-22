import sys
sys.path.append('../ras-secure-message')
from app import application
from app import settings
from sqlalchemy import create_engine
import unittest
from flask import json
from datetime import datetime, timezone

from app.application import app
from flask import current_app
from app.data_model import database


class FlaskTestCase(unittest.TestCase):
    """Test case for application endpoints"""
    @classmethod
    def setUpClass(cls):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
        cls.engine = create_engine('sqlite:////tmp/messages.db', echo=True)
        with app.app_context():
            database.db.init_app(current_app)
            database.db.drop_all()
            database.db.create_all()
            cls.db = database.db

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = application.app.test_client()
        # propagate the exceptions to the test client
        # self.app.testing = True

    def test_health_status(self):
        """sends GET request to the application health monitor endpoint"""
        response = self.app.get('/health')
        """ assert the status code of the response """
        self.assertEqual(response.status_code, 200)

    def test_post_request_all_message_fails(self):
        """sends POST request to the application messageList endpoint"""
        url = "http://localhost:5050/messages"
        response = self.app.post(url)
        self.assertEqual(response.status_code, 405)

    def test_get_request_message(self):
        """sends GET request to the application message by id endpoint"""
        url = "http://localhost:5050/message/21"
        response = self.app.get(url)
        self.assertEqual(json.loads(response.get_data()), {'status': "ok", 'message_id': 21})

    def test_post_request_message_goes_to_database(self):
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
                'create_date': datetime.now(timezone.utc),
                'read_date': datetime.now(timezone.utc)}

        response = self.app.post(url, data=json.dumps(data), headers=headers)
        self.assertEqual(json.loads(response.get_data()), {'status': "ok"})

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

        response = self.app.post(url, data=json.dumps(data), headers=headers)

        engine = create_engine(settings.SECURE_MESSAGING_DATABASE_URL, echo=True)

        with engine.connect() as con:
            request = con.execute('SELECT * FROM secure_message') # WHERE id = (SELECT MAX(id) FROM secure_message)')
            for row in request:
                data = {"to": row['msg_to'], "from": row['msg_from'], "subject": row['subject'], "body": row['body']}
                # print("to:", row['msg_to'], "from:", row['msg_from'], "body:", row['body'])
                self.assertEqual({'to': 'richard', 'from': 'torrance', 'subject': 'MyMessage', 'body': 'hello'}, data)
     

    # def tearDown(self):
    #     # Closing down the database
    #     self.db.session.remove()
    #     self.db.drop_all()

if __name__ == '__main__':
    unittest.main()
