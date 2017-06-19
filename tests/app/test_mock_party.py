import unittest
from app.resources import user_by_uuid


class PartyTestCase(unittest.TestCase):

    def test_get_user_details_by_uuid(self):
        """Test that user details are returned using uuids"""

        list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6712']

        user_details = user_by_uuid.get_details_by_uuid(list_uuids)

        self.assertEqual(user_details[list_uuids[0]], '{"firstname": "Bhavana", "surname": "Lincoln", "telephone": "+443069990888", "status": "ACTIVE"}')

    def test_get_user_details_by_uuids(self):
        """Test that user details are returned using uuids"""

        list_uuids = ['f62dfda8-73b0-4e0e-97cf-1b06327a6712', '01b51fcc-ed43-4cdb-ad1c-450f9986859b', 'dd5a38ff-1ecb-4634-94c8-2358df33e614']

        user_details = user_by_uuid.get_details_by_uuid(list_uuids)

        self.assertEqual(user_details[list_uuids[0]], '{"firstname": "Bhavana", "surname": "Lincoln", "telephone": "+443069990888", "status": "ACTIVE"}')
        self.assertEqual(user_details[list_uuids[1]], '{"firstname": "Chandana", "surname": "Blanchet", "telephone": "+443069990854", "status": "ACTIVE"}')
        self.assertEqual(user_details[list_uuids[2]], '{"firstname": "Ida", "surname", "Larue", "telephone": "+443069990250", "status": "ACTIVE"}')

if __name__ == '__main__':
    unittest.main()
