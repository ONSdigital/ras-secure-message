from app.domain_model.domain import MessageSchema
import unittest
from io import StringIO
from app import application
import sys
sys.path.append('../ras-secure-message')

saved_stdout = sys.stdout


class LoggingTestCase(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = application.app.test_client()

    def test_loggingmessageendpoint(self):
        out = StringIO()
        sys.stdout = out
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        schema.load(message)
        output = out.getvalue().strip()
        self.assertTrue(output, "event='Build message'")

    def test_sendmessage_endpoint(self):
        message = {'msg_to': 'tej', 'msg_from': 'gemma', 'body': 'hello'}
        headers = {'Content-Type': 'application/json'}
        self.app.post('/message/send', data=message, headers=headers)

if __name__ == '__main__':
    unittest.main()
