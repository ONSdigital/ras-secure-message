import json
import requests
import unittest
from unittest import mock

from secure_message.application import create_app
from secure_message.services.case_service import CaseService


class CaseServiceTestHelper:
    def __init__(self, status_code, reason, text):
        self.status_code = status_code
        self.reason = reason
        self.text = text


class CaseServiceTestCase(unittest.TestCase):
    """Test cases for case service"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True

    def test_store_case_event_posts_request_to_remote_service(self):
        """Test store_case_event sends a request and returns data"""
        sut = CaseService()
        case_event_data = CaseServiceTestHelper(200, 'OK', '{"something": "else"}')
        requests.post = mock.Mock(name='post', return_value=case_event_data)

        with self.app.app_context():
            result_data, result_status = sut.store_case_event('1234', 'user')

        self.assertEqual(result_data, json.loads(case_event_data.text))
        self.assertEqual(result_status, 200)

    def test_store_case_event_posts_request_with_error_in_dict(self):
        """Test store_case_event sends a request and returns data"""
        sut = CaseService()
        case_event_data = CaseServiceTestHelper(200, 'OK', '{"error": {"error1":"TestError"}}')
        requests.post = mock.Mock(name='post', return_value=case_event_data)

        with self.app.app_context():
            result_data, result_status = sut.store_case_event('1234', 'user')

        self.assertEqual(result_data, {"error1": "TestError"})
        self.assertEqual(result_status, 200)

    def test_store_case_event_no_case_id_log_error_as_expected(self):
        """Tests that the logger is called with the correct information if store case event called without a case id """
        sut = CaseService()
        case_event_data = CaseServiceTestHelper(200, 'OK', '{"error": {"error1":"TestError"}}')
        requests.post = mock.Mock(name='post', return_value=case_event_data)

        with self.assertLogs(level="ERROR") as cm:
            sut.store_case_event('', 'user')

        self.assertIn("No case id for user user, case event not called", cm.output[0])


if __name__ == '__main__':
    unittest.main()
