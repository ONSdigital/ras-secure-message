import unittest
from app.services.service_toggles import case_service
from flask import json


class CaseServiceIntegrationTestCase(unittest.TestCase):
    """Test case for toggling between a service and its mock"""

    @unittest.SkipTest
    def test_requesting_unknown_case_returns_error(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()
        expected = {'message': 'Case not found for case id 5079d645-3e2e-4a0d-8f2a-9bae99ee4588',
                    'code': 'RESOURCE_NOT_FOUND'}
        result, status_code = sut.store_case_event('5079d645-3e2e-4a0d-8f2a-9bae99ee4588', 'Fred')

        del result['timestamp']
        self.assertEqual(status_code, 404)
        self.assertEqual(expected, result)

    @unittest.SkipTest
    def test_requesting_known_case_returns_no_error(self):
        """Post data to case_service"""
        sut = case_service
        sut.use_real_service()

        response_data, status_code = sut.store_case_event('ab548d78-c2f1-400f-9899-79d944b87300', 'Fred')

        self.assertEqual(status_code, 201)
        self.assertEqual(response_data['caseId'], 'ab548d78-c2f1-400f-9899-79d944b87300')
        self.assertEqual(response_data['category'], 'SECURE_MESSAGE_SENT')
        self.assertEqual(response_data['createdBy'], 'Fred')
        self.assertEqual(response_data['description'], 'New Secure Message')


