import sys
import unittest
from io import StringIO

from flask import g

from secure_message import constants
from secure_message.application import create_app
from secure_message.validation.domain import MessageSchema
from secure_message.validation.user import User

sys.path.append('../../ras-secure-message')
saved_stdout = sys.stdout


class LoggingTestCase(unittest.TestCase):
    """Test case for logging"""
    business_id = 'f1a5e99c-8edf-489a-9c72-6cabe6c387fc'
    survey_id = 'cb8accda-6118-4d3b-85a3-149e28960c54'
    msg_from = 'Gemma'

    def setUp(self):
        """creates a test client"""
        self.app = create_app(config='TestConfig')

    def test_logging_message_endpoint(self):
        """logging message endpoint"""
        out = StringIO()
        sys.stdout = out
        message = {'msg_to': [constants.NON_SPECIFIC_INTERNAL_USER], 'msg_from': self.msg_from, 'subject': 'hello', 'body': 'hello world',
                   'thread_id': '', 'business_id': self.business_id, 'survey_id': self.survey_id}
        with self.app.app_context():
            g.user = User('Gemma', 'respondent')
            schema = MessageSchema()
            schema.load(message)
        output = out.getvalue().strip()
        self.assertIsNotNone(output)


if __name__ == '__main__':
    unittest.main()
