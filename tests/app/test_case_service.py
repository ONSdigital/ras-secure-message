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
                      f"{self.app.config['RM_CASE_SERVICE']}cases/1234/events",
                      json={"something": "else"},
                      status=201)
        sut = CaseService()

        with self.app.app_context():
            result_status = sut.store_case_event('1234', 'user')

        self.assertEqual(result_status, 201)


if __name__ == '__main__':
    unittest.main()
