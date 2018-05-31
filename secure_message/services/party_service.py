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
        ru_dict = None
        payload = urlencode([("id", x) for x in rus])

        party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses",
                                  auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
        if party_data.status_code == 200:
            ru_dict = party_data.json()
            logger.debug(f"Party data retrieved for ru:{rus}")
        else:
            logger.debug(f"Party data failed for ru:{rus}", status_code=party_data.status_code, text=party_data.text,
                         ru=rus)

        return ru_dict

    @staticmethod
    def get_user_details(uuid):

        ru_dict = None
        payload = urlencode([("id", x) for x in uuid])

        party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents",
                                  auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
        if party_data.status_code == 200:
            ru_dict = party_data.json()
            logger.debug(f"Party data retrieved for uuid:{uuid}")
        else:
            logger.error(f'Party service failed for uuid:{uuid}', status_code=party_data.status_code,
                         text=party_data.text,
                         uuid=uuid)

        return ru_dict
