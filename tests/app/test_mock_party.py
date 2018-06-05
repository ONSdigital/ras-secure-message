import unittest

from secure_message.application import create_app
from secure_message.api_mocks.party_service_mock import PartyServiceMock
from secure_message.services.service_toggles import internal_user_service, case_service, party


class PartyTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        internal_user_service.use_mock_service()
        case_service.use_mock_service()
        party.use_mock_service()

    def test_get_business_details_by_ru(self):
        """Test get details for one business using ru_id"""

        list_ru = ['f1a5e99c-8edf-489a-9c72-6cabe6c387fc']

        business_details = party.get_business_details(list_ru)

        self.assertEqual(business_details[0]['id'], list_ru[0])
        self.assertEqual(business_details[0]['name'], "Apple")

    def test_get_business_details_multiple_ru(self):
        """Test business details are returned for multiple ru's"""

        list_ru = ['0a6018a0-3e67-4407-b120-780932434b36',
                   'f1a5e99c-8edf-489a-9c72-6cabe6c387fc',
                   'c614e64e-d981-4eba-b016-d9822f09a4fb',
                   'b3ba864b-7cbc-4f44-84fe-88dc018a1a4c'
                   ]

        business_details = party.get_business_details(list_ru)

        self.assertEqual(business_details[0]['id'], list_ru[2])
        self.assertEqual(business_details[1]['id'], list_ru[1])
        self.assertEqual(business_details[2]['id'], list_ru[0])
        self.assertEqual(business_details[3]['id'], list_ru[3])

    def test_get_user_details_returns_none_if_uuid_not_known(self):
        user = 'SomeoneWhoClearlyDoesNotExist'
        sut = PartyServiceMock()
        result_data = sut.get_user_details(user)
        self.assertIsNone(result_data)

    def test_get_business_details_returns_none_if_ru_not_known(self):
        uuid = 'ABusinessThatDoesNotExist'
        sut = PartyServiceMock()
        result_data = sut.get_business_details(uuid)
        self.assertEqual(result_data, [])


if __name__ == '__main__':
    unittest.main()
