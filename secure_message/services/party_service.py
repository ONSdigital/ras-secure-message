import logging
from urllib.parse import urlencode

from flask import current_app
import requests
from requests import HTTPError
from structlog import wrap_logger
logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    @staticmethod
    def get_business_details(ru_ids):
        """Retrieves the business details from the party service"""
        params = urlencode([("id", ru_id) for ru_id in ru_ids])
        response = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/businesses",
                                auth=current_app.config['BASIC_AUTH'], verify=False, params=params)
        try:
            response.raise_for_status()
        except HTTPError:
            logger.debug("Business detail retrieval failed", status_code=response.status_code, text=response.text,
                         ru_ids=ru_ids)
            return []

        logger.debug("Business details sucessfully retrieved", ru_ids=ru_ids)
        return response.json()

    def get_user_details(self, uuid):
        """Retrieves the user details from the party service for a single uuid"""
        return self._get_user_details_from_party_service([uuid])

    def get_users_details(self, uuids):
        """Retrieves the user details from the party service"""
        return self._get_user_details_from_party_service(uuids)

    @staticmethod
    def _get_user_details_from_party_service(uuids):
        params = urlencode([("id", uuid) for uuid in uuids])
        response = requests.get(f"{current_app.config['RAS_PARTY_SERVICE']}party-api/v1/respondents",
                                auth=current_app.config['BASIC_AUTH'], verify=False, params=params)
        try:
            response.raise_for_status()
        except HTTPError:
            logger.exception('Failed to retrieve data from party service',
                             status_code=response.status_code,
                             text=response.text,
                             uuids=uuids)
            return []

        logger.debug("Party data successfully retrieved", uuids=uuids)
        return response.json()
