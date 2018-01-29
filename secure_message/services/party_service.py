import logging

from flask import current_app, json
import requests
from structlog import wrap_logger

from secure_message import constants

logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    users_cache = dict()
    business_details_cache = dict()

    @staticmethod
    def get_url(api_param, code):
        """
        :param api_param:  is the key configuration that that represent part or the URI .
        :param code: is the code to use in the url ( uuid or ru )
        :return: a formatted url
        """
        if current_app.config[api_param] is None or current_app.config['RAS_PARTY_SERVICE'] is None:
            raise KeyError("%s not present" % api_param)
        return current_app.config[api_param].format(current_app.config['RAS_PARTY_SERVICE'], code)

    def get_business_details(self, ru):
        """Retrieves the business details from the party service"""

        if ru not in self.business_details_cache:
            party_data = requests.get(PartyService.get_url('RAS_PARTY_GET_BY_BUSINESS', ru),
                                      auth=current_app.config['BASIC_AUTH'], verify=False)
            self.users_cache.update(ru, party_data)
        else:
            party_data = self.users_cache.get(ru)

        if party_data.status_code == 200:
            party_dict = json.loads(party_data.text)
            return party_dict, party_data.status_code

        logger.error('Party service failed', status_code=party_data.status_code, text=party_data.text, ru=ru)
        return party_data.text, party_data.status_code

    def get_user_details(self, uuid):
        """
        :param uuid:
        :return: Return user details , unless user is Bres in which case return constant data
        """
        if uuid == constants.BRES_USER:
            party_dict = {"id": constants.BRES_USER,
                          "firstName": "BRES",
                          "lastName": "",
                          "emailAddress": "",
                          "telephone": "",
                          "status": "",
                          "sampleUnitType": "BI"}
            logger.info("UUID is BRES")
            return party_dict, 200

        if uuid not in self.users_cache:
            logger.info("Executing call to the  party service ")
            party_data = requests.get(PartyService.get_url('RAS_PARTY_GET_BY_RESPONDENT', uuid),
                                      auth=current_app.config['BASIC_AUTH'], verify=False)
            self.users_cache.update(uuid, party_data)
        else:
            party_data = self.users_cache.get(uuid)

        if party_data.status_code == 200:
            party_dict = json.loads(party_data.text)
            return party_dict, party_data.status_code

        logger.error('Party service failed', status_code=party_data.status_code, text=party_data.text, uuid=uuid)
        return party_data.text, party_data.status_code
