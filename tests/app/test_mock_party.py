import unittest

from secure_message.application import create_app
from secure_message.api_mocks.party_service_mock import PartyServiceMock
from secure_message.services.service_toggles import internal_user_service, party


class PartyTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        internal_user_service.use_mock_service()
        party.use_mock_service()

    def test_get_business_details_by_business_id(self):
        """Test get details for one business using business_id"""

        list_business_id = ['f1a5e99c-8edf-489a-9c72-6cabe6c387fc']

        business_details = party.get_business_details(list_business_id)

        self.assertEqual(business_details[0]['id'], list_business_id[0])
        self.assertEqual(business_details[0]['name'], "Apple")

    def test_get_business_details_multiple_business_id(self):
        """Test business details are returned for multiple business_id's"""

        list_business_id = ['0a6018a0-3e67-4407-b120-780932434b36',
                            'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                            'c614e64e-d981-4eba-b016-d9822f09a4fb',
                            'b3ba864b-7cbc-4f44-84fe-88dc018a1a4c']

        business_details = party.get_business_details(list_business_id)

        for detail in business_details:
            self.assertIn(detail['id'], list_business_id)

    def test_get_user_details_returns_none_if_uuid_not_known(self):
        user = 'SomeoneWhoClearlyDoesNotExist'
        sut = PartyServiceMock()
        result_data = sut.get_user_details(user)
        self.assertIsNone(result_data)

    def test_get_business_details_returns_none_if_business_id_not_known(self):
        uuid = 'ABusinessThatDoesNotExist'
        sut = PartyServiceMock()
        result_data = sut.get_business_details(uuid)
        self.assertEqual(result_data, [])

    def test_get_does_user_have_claim_returns_true_if_known(self):
        user_id = "ab123456-ce17-40c2-a8fc-abcdef123456"
        business_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
        survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
        sut = PartyServiceMock()
        result = sut.does_user_have_claim(user_id, business_id, survey_id)
        self.assertTrue(result)

    def test_get_does_user_have_claim_returns_false_for_unknown_business_id(self):
        user_id = "ab123456-ce17-40c2-a8fc-abcdef123456"
        business_id = "somethingunknown"
        survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
        sut = PartyServiceMock()
        result = sut.does_user_have_claim(user_id, business_id, survey_id)
        self.assertFalse(result)

    def test_get_does_user_have_claim_returns_false_for_unknown_survey_id(self):
        user_id = "ab123456-ce17-40c2-a8fc-abcdef123456"
        business_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
        survey_id = "not known"
        sut = PartyServiceMock()
        result = sut.does_user_have_claim(user_id, business_id, survey_id)
        self.assertFalse(result)

    def test_get_does_user_have_claim_returns_false_for_not_active_user(self):
        user_id = "inactive_user"
        business_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
        survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
        sut = PartyServiceMock()
        result = sut.does_user_have_claim(user_id, business_id, survey_id)
        self.assertFalse(result)

    def test_get_does_user_have_claim_returns_false_for_not_enabled(self):
        user_id = "not_enabled"
        business_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
        survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
        sut = PartyServiceMock()
        result = sut.does_user_have_claim(user_id, business_id, survey_id)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
