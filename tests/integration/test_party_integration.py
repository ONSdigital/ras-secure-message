import unittest

from secure_message.services.service_toggles import party


class PartyServiceIntegrationTestCase(unittest.TestCase):
    """Test case for toggling between a service and its mock"""

    @unittest.SkipTest
    def test_calling_get_business_data_for_non_existent_business_returns_expected_message(self):
        """Asking for business not in test data gives expected response"""
        sut = party
        sut.use_real_service()
        expected = {"errors": "Business with party id '0a6018a0-3e67-4407-b120-780932434b36' does not exist."}
        result, status_code = sut.get_business_details('0a6018a0-3e67-4407-b120-780932434b36')
        self.assertEqual(result, expected)

    @unittest.SkipTest
    def test_calling_get_business_data_for_invalid_format_id_returns_expected_message(self):
        """Using invalid format_for_id gives expected error """
        sut = party
        sut.use_real_service()
        expected = {"errors": "'14900000000' is not a valid UUID format for property 'id'."}
        result, status_code = sut.get_business_details('14900000000')

        self.assertEqual(result, expected)

    @unittest.SkipTest
    def test_calling_get_business_data_returns_expected_message(self):
        """Using id expected in test data results in expected data returned"""
        sut = party
        sut.use_real_service()

        expected = {'region': 'DE',
                    'formtype': '0001',
                    'runame3': 'Ratchets 00 Ltd',
                    'runame1': 'Bolts',
                    'cell_no': 1,
                    'frotover': 50,
                    'entrepmkr': 'C',
                    'checkletter': 'A',
                    'tradstyle3': 'TRADSTYLE3',
                    'froempment': 50,
                    'tradstyle1': 'TRADSTYLE1',
                    'frosic92': '11111',
                    'associations':
                                [
                                    {'partyId': '4dc25505-e094-4ab6-9379-a9b7881cf3f1',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'ENABLED',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     },
                                    {'partyId': '0e2e030b-6138-411d-9178-9b35e7a47fca',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'ENABLED',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     },
                                    {'partyId': '0e1274ad-7b20-4a3e-856f-1b990ed747cf',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'ENABLED',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     },
                                    {'partyId': '4dbf6572-bdd6-4739-829d-b43e7663dfb6',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'ENABLED',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     },
                                    {'partyId': '4a6cd0da-e010-4e56-8f34-bff9419b24c2',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'ENABLED',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     },
                                    {'partyId': 'dfb8dd8d-aedb-4783-8c09-e88a007d23ae',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'PENDING',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     },
                                    {'partyId': '8be7858e-d2b7-41b5-a937-dfb65802d741',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'ENABLED',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     },
                                    {'partyId': '8f17633a-057b-44de-897b-1c819e3271dc',
                                     'enrolments':
                                        [
                                            {'surveyId': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
                                             'enrolmentStatus': 'ENABLED',
                                             'name': 'Business Register and Employment Survey'
                                             }
                                        ]
                                     }
                                ],
                    'entref': '1234567890',
                    'currency': 'H',
                    'name': 'Bolts and Ratchets 00 Ltd',
                    'ruref': '49900000000',
                    'entname1': 'ENTNAME1',
                    'id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
                    'rusic2007': '11111',
                    'runame2': 'and',
                    'seltype': 'F',
                    'inclexcl': 'G',
                    'entname3': 'ENTNAME3',
                    'tradstyle2': 'TRADSTYLE2',
                    'entname2': 'ENTNAME2',
                    'sampleUnitRef': '49900000000',
                    'birthdate': '01/09/1993',
                    'frosic2007': '11111',
                    'sampleUnitType': 'B',
                    'legalstatus': 'B'
                    }
        result, status_code = sut.get_business_details('3b136c4b-7a14-4904-9e01-13364dd7b972')

        self.assertTrue(result == expected)

    @unittest.SkipTest
    def test_calling_get_user_data_for_non_existent_user_returns_expected_message(self):
        """test non existi=ant user returns expected error message"""

        sut = party
        sut.use_real_service()
        expected = {"errors": "Respondent with party id '0a6018a0-3e67-4407-b120-780932434b36' does not exist."}
        result, status_code = sut.get_user_details('0a6018a0-3e67-4407-b120-780932434b36')
        self.assertEqual(result, expected)

    def test_calling_get_respondent_data_with_expected_test_data_returns_expected_message(self):
        """Test expected test user data returned when requested"""
        sut = party
        sut.use_real_service()
        expected = {"id": "db036fd7-ce17-40c2-a8fc-932e7c228397",
                    "emailAddress": "testuser@email.com",
                    "firstName": "Test",
                    "lastName": "User",
                    "telephone": "1234",
                    "status": "CREATED",
                    "sampleUnitType": "BI"
                    }
        result, status_code = sut.get_user_details('db036fd7-ce17-40c2-a8fc-932e7c228397')
        self.assertEqual(result, expected)
