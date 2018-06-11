import logging
from urllib.parse import urlencode

from flask import current_app
import requests
from requests import HTTPError
from structlog import wrap_logger
logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    def __init__(self):
        self._users_cache = []

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
        """Retrieves the user details from the party service"""
        user_list = None
        if self._users_cache:
            user_list = self._users_cache
        if user_list is None:
            payload = urlencode([("id", x) for x in uuid])

            party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents",
                                      auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
            try:
                party_data.raise_for_status()
            except HTTPError:
                logger.exception('Failed to retrieve data from party service',
                                 status_code=party_data.status_code,
                                 text=party_data.text,
                                 uuid=uuid)
                return user_list

            user_list = party_data.json()
            self._users_cache = user_list
            logger.debug("Party data successfully retrieved", uuid=uuid)

        return user_list
