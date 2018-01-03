import logging

from flask import current_app, json
import requests
from structlog import wrap_logger

from secure_message import constants

logger = wrap_logger(logging.getLogger(__name__))


class PartyService:
    @staticmethod
    def get_business_details(ru):
        """Retrieves the business details from the party service"""

        url = current_app.config['RAS_PARTY_GET_BY_BUSINESS'].format(current_app.config['RAS_PARTY_SERVICE'], ru)
        party_data = requests.get(url, auth=current_app.config['BASIC_AUTH'], verify=False)

        logger.debug('Party service get business details result',
                     status_code=party_data.status_code,
                     reason=party_data.reason,
                     text=party_data.text,
                     url=url)

        if party_data.status_code == 200:
            party_dict = json.loads(party_data.text)
            return party_dict, party_data.status_code
        else:
            logger.error('Party service failed', status_code=party_data.status_code, text=party_data.text, ru=ru)
            return party_data.text, party_data.status_code

    @staticmethod
    def get_user_details(uuid):
        """Return user details , unless user is Bres in which case return constant data"""
        if uuid == constants.BRES_USER:
            party_dict = {"id": constants.BRES_USER,
                          "firstName": "BRES",
                          "lastName": "",
                          "emailAddress": "",
                          "telephone": "",
                          "status": "",
                          "sampleUnitType": "BI"}
            return party_dict, 200
        else:
            url = current_app.config['RAS_PARTY_GET_BY_RESPONDENT'].format(current_app.config['RAS_PARTY_SERVICE'], uuid)
            party_data = requests.get(url,
                                      auth=current_app.config['BASIC_AUTH'],
                                      verify=False)

            logger.debug('Party get user details result',
                         status_code=party_data.status_code,
                         reason=party_data.reason,
                         text=party_data.text,
                         url=url)

            if party_data.status_code == 200:
                party_dict = json.loads(party_data.text)
                return party_dict, party_data.status_code
            else:
                logger.error('Party service failed', status_code=party_data.status_code, text=party_data.text, uuid=uuid)
                return party_data.text, party_data.status_code