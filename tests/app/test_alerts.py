import unittest
from unittest.mock import Mock
from app import settings
from app.common.alerts import AlertUser, AlertViaGovNotify


class AlertsTestCase(unittest.TestCase):
    """Test case for Alerts"""

    @staticmethod
    def test_alert_user_send_if_forwarded_to_alertMethod():
        """sending email notification"""
        sut = AlertUser()
        sut.alertMethod = Mock(AlertViaGovNotify)
        sut.send(settings.NOTIFICATION_DEV_EMAIL, None)
        sut.alertMethod.send.assert_called_with(settings.NOTIFICATION_DEV_EMAIL, None)

    def test_init_with_alerter_params_sets_alert_method(self):
        sut = AlertUser(Mock(AlertViaGovNotify))
        self.assertTrue(isinstance(sut.alertMethod, Mock))

    def test_init_with_alerter_no_params_sets_alert_method_to_AlertViaGovNotify(self):
        sut = AlertUser()
        self.assertTrue(isinstance(sut.alertMethod, AlertViaGovNotify))

if __name__ == '__main__':
    unittest.main()
