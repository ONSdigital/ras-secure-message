from app.domain_model.domain import MessageSchema
import unittest
from io import StringIO
import sys
sys.path.append('../ras-secure-messaging')

saved_stdout = sys.stdout


class test_logging(unittest.TestCase):

    def test_loggingmessageendpoint(self):
        out = StringIO()
        sys.stdout = out
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        schema.load(message)
        output = out.getvalue().strip()
        self.assertTrue(output, "event='Build message'")
        #print("jk")