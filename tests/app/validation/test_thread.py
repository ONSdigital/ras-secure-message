import unittest

from marshmallow import ValidationError

from secure_message.validation.thread import ThreadPatch


class MessageSchemaTestCase(unittest.TestCase):
    """Test case for ThreadPatch"""

    def test_valid_patch_passes_validation(self):
        test_dict = {'category': 'TECHNICAL', 'is_closed': False}
        try:
            ThreadPatch().load(test_dict)
        except ValidationError:
            self.fail("Schema should've been correct and not thrown an error")

    def test_invalid_category_fails_validation(self):
        test_dict = {'category': 'FAIL'}
        with self.assertRaises(ValidationError) as e:
            ThreadPatch().load(test_dict)

        self.assertEqual(e.exception.messages,
                         {'category': ["category can only be one of ['SURVEY', 'TECHNICAL', 'MISC']"]})

    def test_invalid_is_closed_fails_validation(self):
        test_dict = {'is_closed': 'string'}
        with self.assertRaises(ValidationError) as e:
            ThreadPatch().load(test_dict)

        self.assertEqual(e.exception.messages, {'is_closed': ['Not a valid boolean.']})


if __name__ == '__main__':
    unittest.main()
