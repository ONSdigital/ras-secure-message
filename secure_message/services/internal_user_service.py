import json
import logging

from flask import current_app
import requests
from requests import HTTPError
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class InternalUserService:
    @staticmethod
    def get_user_details(uuid):  # NOQA pylint:disable=unused-argument
        """gets the user details from the internal user service"""
        logger.debug("Getting user details from uaa")
        url = f"{current_app.config['UAA_URL']}/Users/{uuid}"
        uaa_token_bytes = current_app.redis_connection['secure-message-client-token']
        uaa_token_str = uaa_token_bytes.decode("utf-8")
        try:
            # Saving to and from redis stops the data retreived from UAA from
            # being valid json.  Fixing the quotes sorts this out.
            uaa_token_str = uaa_token_str.replace("'",'"')
            uaa_token = json.loads(uaa_token_str)
        except ValueError:
            logger.exception("Failed to convert to JSON")
            raise

        token = uaa_token.get('access_token')
        headers = {'Accept': 'application/json',
                  'Authorization': 'Bearer ' + token,
                  'Content-Type': 'application/json'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except HTTPError:
            logger.exception(f"Failed to get user info for {uuid}")
            raise

        try:
            resp_json = response.json()
        except ValueError:
            logger.exception("Failed to decode response JSON.")
            raise

        try:
            user_details =  {
                "id": uuid,
                "firstName": resp_json['name']['givenName'],
                "lastName": resp_json['name']['familyName'],
                "emailAddress": resp_json['emails'][0]['value']
            }
            return user_details
        except KeyError:
            logger.exception("UAA didn't return all expected details")
            raise
