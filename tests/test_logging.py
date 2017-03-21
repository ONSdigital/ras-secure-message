import sys
sys.path.append('../ras-secure-message')
from app.domain_model.domain import MessageSchema
import unittest
from io import StringIO


saved_stdout = sys.stdout


class LoggingTestCase(unittest.TestCase):

    def test_loggingmessageendpoint(self):
        out = StringIO()
        sys.stdout = out
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'subject': 'hello', 'body': 'hello world',
                   'archived': 'archived', 'mark_as_read': 'False'}
        schema = MessageSchema()
        schema.load(message)
        output = out.getvalue().strip()
        self.assertTrue(output, "event='Build message'")
        #print("jk")