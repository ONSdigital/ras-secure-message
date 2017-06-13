import sys
sys.path.append('../../ras-secure-message')
from app.validation.domain import MessageSchema
import unittest
from io import StringIO
from app import application
from testfixtures import log_capture
import logging
from structlog import wrap_logger
from unittest import mock
from app.logger_config import logger_initial_config

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

    def test_basic_logger_config(self):
        """Test logger configuration"""
        with mock.patch('logging.basicConfig') as loggingConfig:
            logger_initial_config(service_name='ras-secure-message', log_level='INFO', logger_format="message", logger_date_format='2017-06-13')
            loggingConfig.assert_called_with(level='INFO', format="message", datefmt='2017-06-13')


if __name__ == '__main__':
    unittest.main()
