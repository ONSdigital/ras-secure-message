import json
import responses
import unittest


from secure_message.application import create_app
from secure_message.services.case_service import CaseService


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
                      self.app.config['RM_CASE_POST'].format(self.app.config['RM_CASE_SERVICE'], '1234'),
                      json={"something": "else"},
                      status=200)
        sut = CaseService()

        with self.app.app_context():
            result_data, result_status = sut.store_case_event('1234', 'user')

        self.assertEqual(result_data, json.loads('{"something": "else"}'))
        self.assertEqual(result_status, 200)

    @responses.activate
    def test_store_case_event_posts_request_with_error_in_dict(self):
        """Test store_case_event sends a request and returns data"""
        responses.add(responses.POST,
                      self.app.config['RM_CASE_POST'].format(self.app.config['RM_CASE_SERVICE'], '1234'),
                      json={"error": {"error1": "TestError"}},
                      status=200)
        sut = CaseService()

        with self.app.app_context():
            result_data, result_status = sut.store_case_event('1234', 'user')

        self.assertEqual(result_data, {"error1": "TestError"})
        self.assertEqual(result_status, 200)

    @responses.activate
    def test_store_case_event_no_case_id_log_error_as_expected(self):
        """Tests that the logger is called with the correct information if store case event called without a case id """
        sut = CaseService()

        responses.add(responses.POST,
                      self.app.config['RM_CASE_POST'].format(self.app.config['RM_CASE_SERVICE'], '1234'),
                      json={"error": {"error2": "TestError"}},
                      status=200)

        with self.assertLogs(level="ERROR") as cm:
            sut.store_case_event('', 'user')

        self.assertIn("No case id for case involving user user, case event not called", cm.output[0])


if __name__ == '__main__':
    unittest.main()
