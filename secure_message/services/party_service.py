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

    def get_business_details(self, rus):
        """Retrieves the business details from the party service"""

        payload = urlencode([("id", x) for x in rus])

        party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses",
                                  auth=current_app.config['BASIC_AUTH'], verify=False, params=payload)
        ru_dict = party_data.json()

        return ru_dict

    def get_user_details(self, uuid):

        user_dict = self._users_cache.get(uuid)

        if user_dict is None:
            logger.info(f"Party Service: retrieve party user data for {uuid}")
            party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents/id/{uuid}",
                                      auth=current_app.config['BASIC_AUTH'], verify=False)
            if party_data.status_code == 200:
                user_dict = party_data.json()
                self._users_cache[uuid] = user_dict
                logger.debug(f"Party data retrieved for uuid:{uuid}")
            else:
                logger.error(f'Party service failed for uuid:{uuid}', status_code=party_data.status_code, text=party_data.text,
                             uuid=uuid)
        return user_dict
