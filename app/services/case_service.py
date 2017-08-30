import logging
from flask import json
import requests
from app import settings
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class CaseService:
    @staticmethod
    def store_case_event(case_id, user_name):
        """posts the data to the case service"""

        json_data = {"description": "New Secure Message",
                     "category": "SECURE_MESSAGE_SENT",
                     "createdBy": user_name
                     }

        url = settings.RM_CASE_POST.format(settings.RM_CASE_SERVICE, case_id)
        case_service_data = requests.post(url, auth=settings.BASIC_AUTH, json=json_data, verify=False)
        logger.debug('case service post result', status_code=case_service_data.status_code,
                     reason=case_service_data.reason, text=case_service_data.text)
        case_service_dict = json.loads(case_service_data.text)
        if 'error' in case_service_dict:
            case_service_dict = case_service_dict['error']

        return case_service_dict, case_service_data.status_code
