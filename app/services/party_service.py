import logging
from flask import Response
from flask import json
import requests
import app.settings

logger = logging.getLogger(__name__)


class PartyService:

    @staticmethod
    def get_business_details(ru):
        """Retrieves the business details from the party service"""
        url = app.settings.RAS_PARTY_GET_BY_BUSINESS.format(app.settings.RAS_PARTY_SERVICE, ru)
        party_data = requests.get(url, verify=False)
        logger.debug('party result => {} {} : {}'.format(party_data.status_code, party_data.reason, party_data.text))
        party_text = json.loads(party_data.text)
        if type(party_text) is list:                    # if id is not a uuid returns a list not a dict
            party_text = {'errors': party_text[0]}
        response = Response(response=json.dumps(party_text), status=party_data.status_code, mimetype="text/html")
        return response

    @staticmethod
    def get_user_details(uuid):
        try:
            return Response(response=json.dumps('To Be replaced When endpoint available', status=200,
                                                mimetype="text/html"))
        except KeyError:
            logger.debug('User ID %s not in mock party service', uuid)
            return Response(response="uuid not valid", status=404,
                            mimetype="text/html")
