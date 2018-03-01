import json
import responses
import unittest

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

    @responses.activate
    def test_store_case_event_posts_request_to_remote_service(self):
        """Test store_case_event sends a request and returns data"""
        responses.add(responses.POST,
                      f"{self.app.config['RM_CASE_SERVICE']}cases/1234/events",
                      json={"something": "else"},
                      status=200)
        sut = CaseService()
        case_event_data = CaseServiceTestHelper(200, 'OK', '{"something": "else"}')

        with self.app.app_context():
            result_data, result_status = sut.store_case_event('1234', 'user')

        self.assertEqual(result_data, json.loads(case_event_data.text))
        self.assertEqual(result_status, 200)

    @responses.activate
    def test_store_case_event_posts_request_with_error_in_dict(self):
        """Test store_case_event sends a request and returns data"""
        responses.add(responses.POST,
                      f"{self.app.config['RM_CASE_SERVICE']}cases/1234/events",
                      json={"error": {"error1": "TestError"}},
                      status=200)
        sut = CaseService()

        with self.app.app_context():
            result_data, result_status = sut.store_case_event('1234', 'user')

        self.assertEqual(result_data, {"error1": "TestError"})
        self.assertEqual(result_status, 200)


if __name__ == '__main__':
    unittest.main()
