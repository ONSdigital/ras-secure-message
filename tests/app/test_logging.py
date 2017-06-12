import sys
sys.path.append('../../ras-secure-message')
from app.validation.domain import MessageSchema
import unittest
from io import StringIO
from app import application
from testfixtures import log_capture
import logging
from structlog import wrap_logger

saved_stdout = sys.stdout


class LoggingTestCase(unittest.TestCase):
    """Test case for logging"""
    def setUp(self):
        """creates a test client"""
        self.app = application.app.test_client()

    def test_logging_message_endpoint(self):
        """logging message endpoint"""
        out = StringIO()
        sys.stdout = out
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'subject': 'hello', 'body': 'hello world',
                   'thread_id': ''}
        schema = MessageSchema()
        schema.load(message)
        output = out.getvalue().strip()
        self.assertIsNotNone(output)

    @log_capture()
    def test_logging_format(self, l):
        """Test logging is in expected format"""
        logger = wrap_logger(logging.getLogger(__name__))
        logger.info('test')
        l.check(
            ('test_logging', 'INFO', "event='test'")
        )


if __name__ == '__main__':
    unittest.main()
