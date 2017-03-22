import sys
sys.path.append('../ras-secure-message')
from app.domain_model.domain import MessageSchema
import unittest
from io import StringIO
from app import application

saved_stdout = sys.stdout


class LoggingTestCase(unittest.TestCase):
    """Test case for logging"""
    def setUp(self):
        # creates a test client
        self.app = application.app.test_client()

    def test_logging_message_endpoint(self):
        """logging message endpoint"""
        out = StringIO()
        sys.stdout = out
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        schema.load(message)
        output = out.getvalue().strip()
        self.assertIsNotNone(output)

if __name__ == '__main__':
    unittest.main()
