import unittest
from app.validation.user import User
from app.authorization.authorizer import Authorizer
from app import constants


class AuthorizerTestCase(unittest.TestCase):
    """Test case for Messages Authorization"""

    def test_internal_is_authorised_to_see_all(self):
        """A user can view a message id they are internal"""
        user = User('1224', 'internal')
        message = {}
        sut = Authorizer()
        expected = True

        result = sut.can_user_view_message(user, message)

        self.assertTrue(expected == result)

    def test_external_user_is_authorised_to_view_msg_if_they_sent_message(self):
        """A respondent can view a message id they sent it """
        user = User('1234', 'external')
        message = {'msg_from': '1234'}
        sut = Authorizer()
        expected = True

        result = sut.can_user_view_message(user, message)

        self.assertTrue(expected == result)

    def test_external_user_is_authorised_to_view_msg_if_they_received_message(self):
        """A respondent is authorised to view a message sent to them """
        user = User('1234', 'external')
        message = {'msg_from': constants.BRES_USER, 'msg_to': ['1111', '1234'], 'labels': ['DRAFT']}
        sut = Authorizer()
        expected = True

        result = sut.can_user_view_message(user, message)

        self.assertTrue(expected == result)

    def test_external_user_is_not_authorised_to_view_msg_if_message_in_DRAFT_INBOX(self):
        """A respondent is authorised to view a message sent to them """
        user = User('1234', 'external')
        message = {'msg_id': '1234567890', 'msg_from': constants.BRES_USER,
                   'msg_to': ['1111', '1234'], 'labels': ['DRAFT_INBOX']}
        sut = Authorizer()
        expected = False

        result = sut.can_user_view_message(user, message)

        self.assertTrue(expected == result)

    def test_external_user_is_not_authorised_to_view_msg_if_they_niether_sent_or_received_it(self):
        """A respondent is not authorised to view a message they niether sent or received"""
        user = User('1234', 'external')
        message = {'msg_id': '1234567890', 'msg_from': constants.BRES_USER, 'msg_to': ['1111', '2222']}
        sut = Authorizer()
        expected = False

        result = sut.can_user_view_message(user, message)

        self.assertTrue(expected == result)

