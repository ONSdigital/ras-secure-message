import unittest
from unittest import mock
from unittest.mock import Mock

from secure_message.application import create_app
from secure_message.exception.exceptions import RasNotifyException
from secure_message.common.alerts import AlertUser, AlertViaGovNotify


class AlertsTestCase(unittest.TestCase):
    """Test case for Alerts"""

    def setUp(self):
        """setup test environment"""
        self.app = create_app()
        self.app.testing = True

    def test_alert_user_send_if_forwarded_to_alert_method(self):
        """sending email notification"""
        sut = AlertUser(Mock(AlertViaGovNotify))
        sut.send(self.app.config['NOTIFICATION_DEV_EMAIL'], None)
        sut.alert_method.send.assert_called_with(self.app.config['NOTIFICATION_DEV_EMAIL'], None)

    def test_init_with_alerter_params_sets_alert_method(self):
        """test uses alert_method from constructor if provided"""
        sut = AlertUser(Mock(AlertViaGovNotify))
        self.assertTrue(isinstance(sut.alert_method, Mock))

    def test_init_with_alerter_no_params_sets_alert_method_to_alert_via_gov_notify(self):
        """test uses AlertViaGovNotify if no alert_method specified"""
        sut = AlertUser()
        self.assertTrue(isinstance(sut.alert_method, AlertViaGovNotify))

    @mock.patch('requests.post')
    def test_post_to_notify_gateway_with_correct_params(self, mock_notify_gateway_post):
        mock_response = mock.Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1}
        mock_notify_gateway_post.return_value = mock_response

        alert_user = AlertUser(AlertViaGovNotify)
        with self.app.app_context():
            alert_user.send('test@email.com', 'myReference')

        mock_notify_gateway_post.assert_called_once_with(
            'http://localhost:8151/emails/test_notification_template_id',
            auth=("admin", "secret"), json={"emailAddress": "test@email.com", "reference": "myReference"},
            timeout=20)

    @mock.patch('requests.post')
    def test_post_to_notify_gateway_throws_exception(self, mock_notify_gateway_post):
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_notify_gateway_post.return_value = mock_response

        alert_user = AlertUser(AlertViaGovNotify)

        with self.app.app_context(), self.assertRaises(RasNotifyException):
            alert_user.send('test@email.com', 'myReference')

        mock_notify_gateway_post.assert_called_once_with(
            'http://localhost:8151/emails/test_notification_template_id',
            auth=("admin", "secret"), json={"emailAddress": "test@email.com", "reference": "myReference"},
            timeout=20)


if __name__ == '__main__':
    unittest.main()
