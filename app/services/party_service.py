import logging
from flask import json
import requests
import app.settings
from app import constants

logger = logging.getLogger(__name__)


class PartyService:

    @staticmethod
    def get_business_details(ru):
        """Retrieves the business details from the party service"""

        url = app.settings.RAS_PARTY_GET_BY_BUSINESS.format(app.settings.RAS_PARTY_SERVICE, ru)
        party_data = requests.get(url, verify=False)
        logger.debug('party get business details result => {} {} : {}'.format(party_data.status_code, party_data.reason,
                                                                              party_data.text))
        party_dict = json.loads(party_data.text)
        if type(party_dict) is list:                    # if id is not a uuid returns a list not a dict
            party_dict = {'errors': party_dict[0]}

        return party_dict, party_data.status_code

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
            url = app.settings.RAS_PARTY_GET_BY_RESPONDENT.format(app.settings.RAS_PARTY_SERVICE, uuid)
            party_data = requests.get(url, verify=False)
            logger.debug('party get user details result => {} {} : {}'.format(party_data.status_code,
                                                                              party_data.reason, party_data.text))
            party_dict = json.loads(party_data.text)
            return party_dict, party_data.status_code
