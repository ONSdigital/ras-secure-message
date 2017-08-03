import logging
from flask import Response
from flask import json

logger = logging.getLogger(__name__)



def business_details_endpoint(ru):
    try:
        return Response(response=json.dumps(_business_details[ru]), status=200, mimetype="text/html")
    except KeyError:
        logger.debug('RU %s not in mock party service.', ru)
        return Response(response="ru is not valid", status=404,
                        mimetype="text/html")


def user_details_endpoint(uuid):
    try:
        return Response(response=json.dumps(_respondent_ids[uuid]), status=200, mimetype="text/html")
    except KeyError:
        logger.debug('User ID %s not in mock party service', uuid)
        return Response(response="uuid not valid", status=404,
                        mimetype="text/html")


_business_details = {}

_business_details['c614e64e-d981-4eba-b016-d9822f09a4fb'] = {"ru_id": "c614e64e-d981-4eba-b016-d9822f09a4fb", "name": "AOL"}
_business_details['f1a5e99c-8edf-489a-9c72-6cabe6c387fc'] = {"ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc", "name": "Apple"}
_business_details['7fc0e8ab-189c-4794-b8f4-9f05a1db185b'] = {"ru_id": "7fc0e8ab-189c-4794-b8f4-9f05a1db185b", "name": "Apricot"}
_business_details['0a6018a0-3e67-4407-b120-780932434b36'] = {"ru_id": "0a6018a0-3e67-4407-b120-780932434b36", "name": "Asparagus"}



_respondent_ids = {}

_respondent_ids['f62dfda8-73b0-4e0e-97cf-1b06327a6712'] = {"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712", "firstname": "Bhavana", "lastName": "Lincoln",
                                                          "email": "lincoln.bhavana@gmail.com", "telephone": "+443069990888", "status": "ACTIVE"}
_respondent_ids['ce12b958-2a5f-44f4-a6da-861e59070a31'] = {"id": "ce12b958-2a5f-44f4-a6da-861e59070a31", "firstname": "Lars", "lastName": "McEachern",
                                                          "email": "mclars@yahoo.com", "telephone": "+443069990413", "status": "ACTIVE"}
_respondent_ids['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'] = {"id": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882", "firstname": "Vana", "lastName": "Oorschot",
                                                          "email": "vana123@aol.com", "telephone": "+443069990289", "status": "ACTIVE"}
_respondent_ids['01b51fcc-ed43-4cdb-ad1c-450f9986859b'] = {"id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b", "firstname": "Chandana", "lastName": "Blanchet",
                                                          "email": "cblanc@hotmail.co.uk", "telephone": "+443069990854", "status": "ACTIVE"}
_respondent_ids['dd5a38ff-1ecb-4634-94c8-2358df33e614'] = {"id": "dd5a38ff-1ecb-4634-94c8-2358df33e614", "firstname": "Ida", "lastName": "Larue",
                                                          "email": "ilarue47@yopmail.com", "telephone": "+443069990250", "status": "ACTIVE"}
_respondent_ids['BRES'] = {"id": "BRES", "firstname": "BRES", "lastName": "", "email": "", "telephone": "", "status": ""}
_respondent_ids['AnotherSurvey'] = {"id": "AnotherSurvey", "firstname": "AnotherSurvey", "lastName": "", "email": "", "telephone": "", "status": ""}

_respondent_ids['ce12b958-2a5f-44f4-a6da-861e59070a32'] = {"id": "ce12b958-2a5f-44f4-a6da-861e59070a32", "firstname": "Liz", "lastName": "Larkin",
                                                          "email": "ilarue47@yopmail.com", "telephone": "+443069990250", "status": "ACTIVE"}

_respondent_ids['db036fd7-ce17-40c2-a8fc-932e7c228397'] = {"id": "db036fd7-ce17-40c2-a8fc-932e7c228397", "firstname" : "Peter", "lastName" : "Smith",
                                                            "email": "peter.smith@hostmail.com", "telephone" : "+447894056785", "status" : "ACTIVE"}
