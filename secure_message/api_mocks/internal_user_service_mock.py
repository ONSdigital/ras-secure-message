import logging

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class InternalUserServiceMock:
    def __init__(self):
        self.internal_user_dict = {"Someuuid": {"id": "Someuuid", "firstName": "fred", "lastName": "flinstone",
                                                "emailAddress": "mock@email.com"},
                                   "01b51fcc-ed43-4cdb-ad1c-450f9986859b": {
                                       "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
                                       "firstName": "fred", "lastName": "flinstone", "emailAddress": "mock@email.com"},
                                   "f62dfda8-73b0-4e0e-97cf-1b06327a6712": {
                                       "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
                                       "firstName": "fred", "lastName": "flinstone", "emailAddress": "mock@email.com"},
                                   "Tej": {"id": "Tej", "firstName": "Tejas", "lastName": "patel",
                                           "emailAddress": "mock@email.com"},
                                   "BRES": {"id": "TRES", "firstName": "BRES", "lastName": "",
                                            "emailAddress": "mock@email.com"},
                                   "SomeStringUntilWeGetIds": {"id": "SomeStringUntilWeGetIds",
                                                               "firstName": "MadeUpUser", "lastName": "",
                                                               "emailAddress": "mock@email.com"}
                                   }

    def get_user_details(self, uuid):
        """gets the user details from the internal user service"""
        logger.debug("getting mock user details for uaa")
        if uuid:
            found = self.internal_user_dict.get(uuid)
            if found:
                return found, 200
        return "error retrieving details", 404
