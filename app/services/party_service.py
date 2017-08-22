import logging
from flask import Response
from flask import json
import requests
import app.settings
from app import constants
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    @staticmethod
    def get_business_details(ru):
        """Retrieves the business details from the party service"""
        url = app.settings.RAS_PARTY_GET_BY_BUSINESS.format(app.settings.RAS_PARTY_SERVICE, ru)
        party_data = requests.get(url, verify=False)

        logger.debug('Party service get business details result', status_code=party_data.status_code, reason=party_data.reason, text=party_data.text,
                     url=url)

        if party_data.status_code == 200:
            party_text = json.loads(party_data.text)
            if type(party_text) is list:                    # if id is not a uuid returns a list not a dict
                party_text = {'errors': party_text[0]}
            response = Response(response=json.dumps(party_text), status=party_data.status_code, mimetype="text/html")
            return response
        else:
            logger.info('Party (RU) not found', ru=ru)
            return Response(response="uuid not valid", status=404, mimetype="text/html")

    @staticmethod
    def get_user_details(uuid):
        """Return user details , unless user is Bres in which case return constant data"""
        try:
            if uuid == constants.BRES_USER:
                party_dict = {"id": constants.BRES_USER,
                              "firstName": "BRES",
                              "lastName": "",
                              "emailAddress": "",
                              "telephone": "",
                              "status": "",
                              "sampleUnitType": "BI"}
                return Response(response=json.dumps(party_dict), status=200, mimetype="text/html")
            else:
                url = app.settings.RAS_PARTY_GET_BY_RESPONDENT.format(app.settings.RAS_PARTY_SERVICE, uuid)
                party_data = requests.get(url, verify=False)

                logger.debug('Party get user details result', status_code=party_data.status_code, reason=party_data.reason, text=party_data.text,
                             url=url)

                if party_data.status_code == 200:
                    party_dict = json.loads(party_data.text)
                    return Response(response=json.dumps(party_dict), status=party_data.status_code, mimetype="text/html")
                else:
                    logger.error('Party (User ID) not found', user_uuid=uuid)
                    return Response(response="uuid not valid", status=404, mimetype="text/html")

        except KeyError:
            logger.error('User ID not in mock party service', user_uuid=uuid)
            return Response(response="uuid not valid", status=404, mimetype="text/html")
