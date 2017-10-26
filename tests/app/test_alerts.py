import unittest
from unittest.mock import Mock
import mock
from app import settings
from app.common.alerts import AlertUser, AlertViaGovNotify


class AlertsTestCase(unittest.TestCase):
    """Test case for Alerts"""

    @staticmethod
    def test_alert_user_send_if_forwarded_to_alert_method():
        """sending email notification"""
        sut = AlertUser(Mock(AlertViaGovNotify))
        sut.send(settings.NOTIFICATION_DEV_EMAIL, None)
        sut.alert_method.send.assert_called_with(settings.NOTIFICATION_DEV_EMAIL, None)

    def test_init_with_alerter_params_sets_alert_method(self):
        """test uses alert_method from constructor if provided"""
        sut = AlertUser(Mock(AlertViaGovNotify))
        self.assertTrue(isinstance(sut.alert_method, Mock))

    def test_init_with_alerter_no_params_sets_alert_method_to_alert_via_gov_notify(self):
        """test uses AlertViaGovNotify if no alert_method specified"""
        sut = AlertUser()
        self.assertTrue(isinstance(sut.alert_method, AlertViaGovNotify))

    @mock.patch('requests.post')
    def test_post_to_notify_gateway_with_correct_params(self, mock_notify_gateway):
        mock_notify_gateway.return_value = {"id": 1}
        alert_user = AlertUser(AlertViaGovNotify)
        alert_user.send('test@email.com', 'myReference')

        mock_notify_gateway.assert_called_once_with(
            'http://notifygatewaysvc-dev.apps.devtest.onsclofo.uk/emails/test_notification_template_id',
            auth= ("test_user", "test_password"), json={ "emailAddress": "test@email.com", "reference": "myReference"},
            timeout=20)


if __name__ == '__main__':
    unittest.main()
