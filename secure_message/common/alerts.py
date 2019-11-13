import logging
from urllib import parse as urlparse

from flask import current_app
import requests
from structlog import wrap_logger

from secure_message.exception.exceptions import RasNotifyException

logger = wrap_logger(logging.getLogger(__name__))


class AlertViaGovNotify:
    """Notify Api handler"""

    @staticmethod
    def send(email, msg_id, personalisation, survey_id, party_id):

        notification = {
            "emailAddress": email,
            "personalisation": personalisation,
            "reference": msg_id
        }

        url = urlparse.urljoin(current_app.config['NOTIFY_GATEWAY_URL'],
                               current_app.config['NOTIFICATION_TEMPLATE_ID'])

        response = requests.post(url, auth=current_app.config['BASIC_AUTH'],
                                 timeout=current_app.config['REQUESTS_POST_TIMEOUT'], json=notification)

        # If a 500 error does occur, it won't be shown to the user and the exception will just be swallowed
        if response.status_code != 201:
            raise RasNotifyException(code=500, survey_id=survey_id, party_id=party_id)

        logger.info('Sent secure message email notification, via RM Notify-Gateway to GOV.UK Notify.',
                    message_id=response.json()["id"], survey_id=survey_id, party_id=party_id,
                    personalisation=personalisation)


class AlertViaLogging:
    """Alert goes via gov notify (0) or via logs (1)"""

    @staticmethod
    def send(_, msg_id, personalisation, survey_id, party_id):
        logger.info('Email sent', msg_id=msg_id, personalisation=personalisation, survey=survey_id, party_id=party_id)


class AlertUser:
    alert_method = AlertViaGovNotify()

    def __init__(self, alerter=None):
        if alerter is not None:
            self.alert_method = alerter

    def send(self, email, msg_id, personalisation, survey_id=None, party_id=None):
        self.alert_method.send(email, msg_id, personalisation, survey_id=survey_id, party_id=party_id)
