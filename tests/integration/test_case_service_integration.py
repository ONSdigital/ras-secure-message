import unittest
from secure_message.services.service_toggles import case_service


class CaseServiceIntegrationTestCase(unittest.TestCase):
    """Test case for toggling between a service and its mock"""

    @unittest.SkipTest
    def test_requesting_unknown_case_returns_error(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        result, status_code = sut.store_case_event('5079d645-3e2e-4a0d-8f2a-9bae99ee4588', 'Fred')

        self.assertEqual(status_code, 404)

    @unittest.SkipTest
    def test_request_with_no_case_returns_error(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        status_code = sut.store_case_event('', '')

        self.assertEqual(status_code, 500)

    @unittest.SkipTest
    def test_requesting_known_case_returns_no_error(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        status_code = sut.store_case_event('ab548d78-c2f1-400f-9899-79d944b87300', 'Fred')

        self.assertEqual(status_code, 201)

    @unittest.SkipTest
    def test_created_by_under_limit(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        status_code = sut.store_case_event('ab548d78-c2f1-400f-9899-79d944b87300',
                                           'FredFredFredFredFredFredFredFredFredFredFredFred')  # 48 characters
        self.assertEqual(status_code, 201)

    @unittest.SkipTest
    def test_created_by_over_limit(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        status_code = sut.store_case_event('ab548d78-c2f1-400f-9899-79d944b87300',
                                           'FredFredFredFredFredFredFredFredFredFredFredFredFred')  # 52 characters
        self.assertEqual(status_code, 400)

    @unittest.SkipTest
    def test_created_by_is_empty(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        status_code = sut.store_case_event('ab548d78-c2f1-400f-9899-79d944b87300', '')

        self.assertEqual(status_code, 400)

    @unittest.SkipTest
    def test_created_by_is_none(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        status_code = sut.store_case_event('ab548d78-c2f1-400f-9899-79d944b87300', None)

        self.assertEqual(status_code, 400)
