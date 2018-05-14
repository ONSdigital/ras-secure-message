import logging
from flask import current_app
import requests
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class CaseService:
    @staticmethod
    def store_case_event(case_id, user_name, msg_id):
        """posts the data to the case service"""

        if case_id:
            json_data = {"description": "New Secure Message",
                         "category": "SECURE_MESSAGE_SENT",
                         "createdBy": user_name}

            url = f"{current_app.config['RM_CASE_SERVICE']}cases/{case_id}/events"
            case_service_data = requests.post(url, auth=current_app.config['BASIC_AUTH'], json=json_data, verify=False)
            logger.debug('case service post result', status_code=case_service_data.status_code,
                         reason=case_service_data.reason, text=case_service_data.text)
            return case_service_data.status_code

        err = f"No case id for case involving msg_id: {msg_id}, case event not called"
        logger.error(err)
        return {'error': err}, 400
