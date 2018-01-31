import logging

from flask import current_app, json
import requests
from structlog import wrap_logger

from secure_message import constants

logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    __users_cache = dict()
    __business_details_cache = dict()

    @staticmethod
    def get_url(api_param, code):
        try:
            return current_app.config[api_param].format(current_app.config['RAS_PARTY_SERVICE'], code)
        except KeyError:
            raise KeyError(f"{api_param} not present")

    def get_business_details(self, ru):
        """Retrieves the business details from the party service"""

        if ru not in self.__business_details_cache:
            logger.info("Party Service: retrieve party data using", ru=ru)
            party_data = requests.get(PartyService.get_url('RAS_PARTY_GET_BY_BUSINESS', ru),
                                      auth=current_app.config['BASIC_AUTH'], verify=False)
            self.__business_details_cache[ru] = party_data
        else:
            party_data = self.__business_details_cache.get(ru)

        if party_data.status_code == 200:
            party_dict = json.loads(party_data.text)
            return party_dict, party_data.status_code

        logger.error('Party service failed', status_code=party_data.status_code, text=party_data.text, ru=ru)
        return party_data.text, party_data.status_code

    def get_user_details(self, uuid):
        if uuid == constants.BRES_USER:
            party_dict = {"id": constants.BRES_USER,
                          "firstName": "BRES",
                          "lastName": "",
                          "emailAddress": "",
                          "telephone": "",
                          "status": "",
                          "sampleUnitType": "BI"}
            return party_dict, 200

        if uuid not in self.__users_cache:
            logger.info("Party Service: retrieve party data using", uuid=uuid)
            party_data = requests.get(PartyService.get_url('RAS_PARTY_GET_BY_RESPONDENT', uuid),
                                      auth=current_app.config['BASIC_AUTH'], verify=False)
            self.__users_cache[uuid] = party_data
        else:
            party_data = self.__users_cache.get(uuid)

        if party_data.status_code == 200:
            party_dict = json.loads(party_data.text)
            return party_dict, party_data.status_code

        logger.error('Party service failed', status_code=party_data.status_code, text=party_data.text, uuid=uuid)
        return party_data.text, party_data.status_code
