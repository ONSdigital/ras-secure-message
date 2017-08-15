import unittest
from app.services.service_toggles import case_service
from flask import json


class CaseServiceIntegrationTestCase(unittest.TestCase):
    """Test case for toggling between a service and its mock"""

    # @unittest.SkipTest
    def test_post_data_to_case_service(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()
        expected = {"errors": "Case_service id '5079d645-3e2e-4a0d-8f2a-9bae99ee4588' does not exist."}
        response = sut.store_case_event('5079d645-3e2e-4a0d-8f2a-9bae99ee4588')
        self.assertEqual(json.loads(response.data), expected)

