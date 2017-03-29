from app import settings
from notifications_python_client import NotificationsAPIClient
from notifications_python_client import errors
import logging


logger = logging.getLogger(__name__)


class AlertUser:
    """Alert User"""
    def __init__(self, alerter):
        self._alerter = alerter

    def send(self, email, template_id, reference):
        try:
            self._alerter.send(email, template_id, reference)

        except errors.HTTPError as http_error:
            logger.exception(http_error)
            return http_error.status_code, http_error.message[0]
        except BaseException as e:
            logger.exception(e)
            return 400, 'Notification not sent'

        return 201, 'OK'


class AlertViaGovNotify:
    """Notify Api handler"""
    def __init__(self):
        self.notifications_client = NotificationsAPIClient(settings.NOTIFICATION_COMBINED_KEY)

    def send(self, email, template_id, reference):
        self.notifications_client.send_email_notification(
            email_address=email,
            template_id=template_id,
            personalisation=None,
            reference=reference
        )




