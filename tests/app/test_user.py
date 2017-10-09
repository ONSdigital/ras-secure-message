import unittest

from app.validation.user import User


class UserTestCase(unittest.TestCase):
    """Test case for User"""

    def test_is_respondent_true(self):
        """test uses is_respondent property of User with respondent urn"""
        self.assertTrue(User('0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'respondent').is_respondent)

    def test_is_respondent_false(self):
        """test uses is_respondent property of User with internal urn"""
        self.assertFalse(User('ce12b958-2a5f-44f4-a6da-861e59070a31', 'internal').is_respondent)

    def test_is_internal_true(self):
        """test uses is_internal property of User with internal urn"""
        self.assertTrue(User('ce12b958-2a5f-44f4-a6da-861e59070a31', 'internal').is_internal)

    def test_is_internal_false(self):
        """test uses is_internal property of User with respondent urn"""
        self.assertFalse(User('0a7ad740-10d5-4ecb-b7ca-3c0384afb882', 'respondent').is_internal)


if __name__ == '__main__':
    unittest.main()
