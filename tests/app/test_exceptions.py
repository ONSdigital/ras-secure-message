import unittest

from app.exception.exceptions import MessageSaveException, RasNotifyException


class ExceptionsTestCase(unittest.TestCase):
    """Test case for checking custom exceptions"""
    def test_defaults_in_message_save_exception(self):
        save_exception = MessageSaveException("Test")
        self.assertEqual(save_exception.description,"Test")
        self.assertEqual(save_exception.code, 500)

    def test_defaults_in_notify_exception(self):
        notify_exception = RasNotifyException()
        self.assertEqual(notify_exception.code, 500)
        self.assertEqual(notify_exception.description, 'There was a problem sending a notification via RM '
                                                       'Notify-Gateway to GOV.UK Notify')
