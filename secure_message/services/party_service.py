import logging
import ast
from flask import current_app, json
import requests
from structlog import wrap_logger
logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    def __init__(self):
        self._users_cache = {}
        self._business_details_cache = {}

    def get_business_details(self, ru):
        """Retrieves the business details from the party service"""

        ru_dict = self._business_details_cache.get(ru)

        if ru_dict is None:
            logger.info(f"Party Service: retrieve party ru data for {ru}")

            party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses/id/{ru}",
                                      auth=current_app.config['BASIC_AUTH'], verify=False)
            if party_data.status_code == 200:
                ru_dict = json.loads(party_data.text)
                self._business_details_cache[ru] = ru_dict
                logger.debug(f"Party data retrieved for ru:{ru}")
            else:
                logger.debug(f"Party data failed for ru:{ru}", status_code=party_data.status_code, text=party_data.text,
                             ru=ru)

        return ru_dict

    def get_user_details(self, uuid):

        user_dict = self._users_cache.get(uuid)

        if user_dict is None:
            logger.info(f"Party Service: retrieve party user data for {uuid}")
            party_data = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents/id/{uuid}",
                                      auth=current_app.config['BASIC_AUTH'], verify=False)
            if party_data.status_code == 200:
                user_dict = eval(json.loads(json.dumps(party_data.text)))
                self._users_cache[uuid] = user_dict
                logger.debug(f"Party data retrieved for uuid:{uuid}")
            else:
                logger.error(f'Party service failed for uuid:{uuid}', status_code=party_data.status_code, text=party_data.text,
                             uuid=uuid)
        return user_dict
