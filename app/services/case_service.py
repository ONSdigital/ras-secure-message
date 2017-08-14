import logging
from flask import Response
from flask import json
import requests
import app.settings

logger = logging.getLogger(__name__)


class CaseService:
    @staticmethod
    def store_case_event(case_id):
        """posts the data to the case service"""
        url = app.settings.RM_CASE_POST.format(app.settings.RM_CASE_SERVICE, case_id)
        case_service_data = requests.post(url, verify=False)
        logger.debug('case service post result => {} {} : {}'.format(case_service_data.status_code, case_service_data.reason,
                                                                     case_service_data.text))
        case_service_text = json.loads(case_service_data.text)
        if type(case_service_text) is list:  # if id is not a uuid returns a list not a dict
            case_service_text = {'errors': case_service_text[0]}
        response = Response(response=json.dumps(case_service_text), status=case_service_data.status_code, mimetype="text/html")
        return response
