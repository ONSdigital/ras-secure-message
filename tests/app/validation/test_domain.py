import unittest

from marshmallow import ValidationError

from secure_message.validation.domain import MessagePatch


class MessageSchemaTestCase(unittest.TestCase):
    """Test case for ThreadPatch"""

    def test_valid_patch_passes_validation(self):
        test_dict = {'survey_id': '30b97a0c-7efe-4555-8384-2f4f74ebc029',
                     'case_id': '437934d4-9993-48e2-9290-7ab546c91f0b'}
<<<<<<< HEAD
        try:
            MessagePatch().load(test_dict)
        except ValidationError:
            self.fail("Schema should've been correct and not thrown an error")
=======
        schema = MessagePatch(strict=True).load(test_dict)
        self.assertTrue(schema.errors == {})
>>>>>>> origin/main

    def test_invalid_survey_id_fails_validation(self):
        test_dict = {'survey_id': 'FAIL',
                     'case_id': '437934d4-9993-48e2-9290-7ab546c91f0b'}
        with self.assertRaises(ValidationError) as e:
<<<<<<< HEAD
            MessagePatch().load(test_dict)
=======
            MessagePatch(strict=True).load(test_dict)
>>>>>>> origin/main

        self.assertEqual(e.exception.messages, {'survey_id': ["Not a valid UUID."]})

    def test_invalid_empty_survey_id_fails_validation(self):
        test_dict = {'survey_id': '',
                     'case_id': '437934d4-9993-48e2-9290-7ab546c91f0b'}
        with self.assertRaises(ValidationError) as e:
<<<<<<< HEAD
            MessagePatch().load(test_dict)
=======
            MessagePatch(strict=True).load(test_dict)
>>>>>>> origin/main

        self.assertEqual(e.exception.messages, {'survey_id': ["Not a valid UUID."]})


if __name__ == '__main__':
    unittest.main()
