import logging
from flask import Response
from flask import json

logger = logging.getLogger(__name__)


class PartyService:

    def get_business_details(self, ru):
        try:
            return Response(response=json.dumps(self._read_business_details(ru)), status=200, mimetype="text/html")
        except KeyError:
            return Response(response="ru is not valid", status=404,
                            mimetype="text/html")

    def get_user_details(self, uuid):
        try:
            return Response(response=json.dumps(self._read_business_details(uuid)), status=200, mimetype="text/html")
        except KeyError:
            logger.debug('User ID %s not in mock party service', uuid)
            return Response(response="uuid not valid", status=404,
                            mimetype="text/html")

    def _read_business_details(self, ru):
        x=0

    def _read_user_details(self, uuid):
        x=0