import unittest
from app.validation.user import User


class UserTestCase(unittest.TestCase):
    """Test case for User"""

    def test_is_respondent_true(self):
        """test uses is_respondent property of User with respondent urn"""
        self.assertTrue(User('respondent.00000.00000', 'respondent').is_respondent)

    def test_is_respondent_false(self):
        """test uses is_respondent property of User with internal urn"""
        self.assertFalse(User('internal.00000.00000', 'internal').is_respondent)

    def test_is_internal_true(self):
        """test uses is_internal property of User with internal urn"""
        self.assertTrue(User('internal.00000.00000', 'internal').is_internal)

    def test_is_internal_false(self):
        """test uses is_internal property of User with respondent urn"""
        self.assertFalse(User('respondent.00000.00000', 'respondent').is_internal)


if __name__ == '__main__':
    unittest.main()
