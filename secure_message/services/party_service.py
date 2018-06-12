import logging
from urllib.parse import urlencode

from flask import current_app
import requests
from requests import HTTPError
from structlog import wrap_logger
logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    @staticmethod
    def get_business_details(rus):
        """Retrieves the business details from the party service"""
        ru_list = []
        payload = urlencode([("id", x) for x in rus])

        party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses",
                                  auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
        if party_data.status_code == 200:
            ru_list = party_data.json()
            logger.debug(f"Party data retrieved for ru:{rus}")
        else:
            logger.debug(f"Party data failed for ru:{rus}", status_code=party_data.status_code, text=party_data.text,
                         ru=rus)
        return ru_list

    def get_user_details(self, uuid):
        """Retrieves the user details from the party service after converting single
        uuid into a list of one"""
        return self._get_the_user_details([uuid])

    def get_users_details(self, uuids):
        """Retrieves the user details from the party service"""
        return self._get_the_user_details(uuids)

    @staticmethod
    def _get_the_user_details(uuids):
        payload = urlencode([("id", x) for x in uuids])
        response = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents",
                                auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
        try:
            response.raise_for_status()
        except HTTPError:
            logger.exception('Failed to retrieve data from party service',
                             status_code=response.status_code,
                             text=response.text,
                             uuids=uuids)
            return []

        user_list = response.json()
        logger.debug("Party data successfully retrieved", uuids=uuids)

        return user_list
