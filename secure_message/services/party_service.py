import logging
from urllib.parse import urlencode

from flask import current_app
import requests
from requests import HTTPError
from structlog import wrap_logger
logger = wrap_logger(logging.getLogger(__name__))


class PartyService:

    @staticmethod
    def get_business_details(business_ids):
        """Retrieves the business details from the party service"""
        params = urlencode([("id", business_id) for business_id in business_ids])
        response = requests.get(f"{current_app.config['_PARTY_SERVICE']}party-api/v1/businesses",
                                auth=current_app.config['BASIC_AUTH'], verify=False, params=params)
        try:
            response.raise_for_status()
        except HTTPError:
            logger.info("Business detail retrieval failed", status_code=response.status_code, text=response.text,
                        business_ids=business_ids)
            return []

        logger.info("Business details successfully retrieved", business_ids=business_ids)
        return response.json()

    def get_user_details(self, uuid):
        """Retrieves the user details from the party service for a single uuid"""
        return self._get_user_details_from_party_service([uuid])

    def get_users_details(self, uuids):
        """Retrieves the user details from the party service"""
        return self._get_user_details_from_party_service(uuids)

    @staticmethod
    def does_user_have_claim(user_id, business_id, survey_id):
        """Returns true of the user id has a claim on the business_id, survey_id combination
         False if not.

         Rather than inspect the respondent data it defers to Party Service for the precise logic
         to determine what constitutes a valid claim so as to maintain separation of concerns and
         avoid future maintenance issues.
        """
        params = {"respondent_id": user_id, "business_id": business_id, "survey_id": survey_id}

        response = requests.get(f"{current_app.config['PARTY_SERVICE']}party-api/v1/respondents/claim",
                                auth=current_app.config['BASIC_AUTH'], verify=False, params=urlencode(params))
        try:
            response.raise_for_status()
        except HTTPError:
            logger.exception('Failed to validate claim data with party service',
                             status_code=response.status_code,
                             text=response.text,
                             respondent_id=user_id,
                             business_id=business_id,
                             survey_id=survey_id)
            return False

        logger.info("claim response", response_data=response.content)
        claim_response = response.content.decode("utf-8")
        logger.info("Party claim data successfully retrieved ", respondent_id=user_id,
                    business_id=business_id, survey_id=survey_id, response=claim_response)
        return claim_response.lower() == 'valid'

    @staticmethod
    def _get_user_details_from_party_service(uuids):
        params = urlencode([("id", uuid) for uuid in uuids])
        response = requests.get(f"{current_app.config['PARTY_SERVICE']}party-api/v1/respondents",
                                auth=current_app.config['BASIC_AUTH'], verify=False, params=params)
        try:
            response.raise_for_status()
        except HTTPError:
            logger.exception('Failed to retrieve data from party service',
                             status_code=response.status_code,
                             text=response.text,
                             uuids=uuids)
            return []

        logger.info("Party data successfully retrieved", uuids=uuids)
        return response.json()
