import logging

from flask import current_app
import requests
from requests import HTTPError
from structlog import wrap_logger

from secure_message.constants import NON_SPECIFIC_INTERNAL_USER

logger = wrap_logger(logging.getLogger(__name__))


class InternalUserService:
    @staticmethod
    def get_user_details(uuid):
        """gets the user details from the internal user service"""
        if uuid == NON_SPECIFIC_INTERNAL_USER:
            return InternalUserService.get_default_user_details(NON_SPECIFIC_INTERNAL_USER)

        logger.info("Getting user details from uaa", uuid=uuid)
        url = f"{current_app.config['UAA_URL']}/Users/{uuid}"
        uaa_token = current_app.oauth_client_token
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + uaa_token.get('access_token'),
                   'Content-Type': 'application/json'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            resp_json = response.json()
        except HTTPError:
            logger.exception("Failed to get user info", uuid=uuid)
            raise
        except ValueError:
            logger.exception("Failed to decode response JSON", uuid=uuid)
            raise

        try:
            user_details = {
                "id": uuid,
                "firstName": resp_json['name']['givenName'],
                "lastName": resp_json['name']['familyName'],
                "emailAddress": resp_json['emails'][0]['value']
            }
            logger.info("Successfully retrieved and formatted user details", uuid=uuid)
            return user_details
        except KeyError:
            user_details = InternalUserService.get_default_user_details(uuid)
            logger.exception("UAA didn't return all expected details", uuid=uuid)

            return user_details

    @staticmethod
    def get_default_user_details(uuid):
        user_details = {
            "id": uuid,
            "firstName": "ONS",
            "lastName": "User",
            "emailAddress": ""
        }
        return user_details
