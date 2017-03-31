from app import settings
from notifications_python_client import NotificationsAPIClient
import logging

logger = logging.getLogger(__name__)


class AlertUser:
    """Alert User"""
    def __init__(self, alerter):
        self._alerter = alerter

    def send(self, email, template_id, reference):
        self._alerter.send(email, template_id, reference)


class AlertViaGovNotify:
    """Notify Api handler"""
    def __init__(self):
        self.notifications_client = NotificationsAPIClient(settings.NOTIFICATION_COMBINED_KEY)

    def send(self, email, template_id, reference):

        try:
            self.notifications_client.send_email_notification(
                email_address=email,
                template_id=template_id,
                personalisation=None,
                reference=reference
            )
        except BaseException as e:
            logger.info(e)
            raise ValueError(e)


