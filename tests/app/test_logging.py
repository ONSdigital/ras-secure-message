import sys
import unittest
from io import StringIO

from flask import g

from secure_message.validation.domain import MessageSchema
from secure_message.application import create_app
from secure_message.validation.user import User


sys.path.append('../../ras-secure-message')

saved_stdout = sys.stdout


class LoggingTestCase(unittest.TestCase):
    """Test case for logging"""
    def setUp(self):
        """creates a test client"""
        self.app = create_app()

    def test_logging_message_endpoint(self):
        """logging message endpoint"""
        out = StringIO()
        sys.stdout = out
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'subject': 'hello', 'body': 'hello world',
                   'thread_id': ''}
        with self.app.app_context():
            g.user = User('torrence', 'respondent')
            schema = MessageSchema()
            schema.load(message)
        output = out.getvalue().strip()
        self.assertIsNotNone(output)


if __name__ == '__main__':
    unittest.main()
