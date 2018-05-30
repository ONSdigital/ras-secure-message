import logging
from urllib.parse import urlencode

from flask import current_app
import requests
from structlog import wrap_logger
logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    def __init__(self):
        self._users_cache = {}
        self._business_details_cache = {}

    @staticmethod
    def get_business_details(rus):
        """Retrieves the business details from the party service"""

        payload = urlencode([("id", x) for x in rus])

        party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses",
                                  auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
        ru_dict = party_data.json()

        return ru_dict

    @staticmethod
    def get_user_details(uuid):

        payload = urlencode([("id", x) for x in uuid])

        party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents",
                                  auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
        ru_dict = party_data.json()

        return ru_dict
