import logging
from flask import Response
from flask import json
from app import constants

logger = logging.getLogger(__name__)


class PartyServiceMock:

    def get_business_details(self, ru):
        """Return mock business details"""
        try:
            return Response(response=json.dumps(self._business_details[ru]), status=200, mimetype="text/html")
        except KeyError:
            logger.debug('RU %s not in mock party service.', ru)
            return Response(response="ru is not valid", status=404,
                            mimetype="text/html")

    def get_user_details(self, uuid):
        """Return mock user details"""
        try:
            return Response(response=json.dumps(self._respondent_ids[uuid]), status=200, mimetype="text/html")
        except KeyError:
            logger.debug('User ID %s not in mock party service', uuid)
            return Response(response="uuid not valid", status=404,
                            mimetype="text/html")

    _business_details = {'c614e64e-d981-4eba-b016-d9822f09a4fb': {"id": "c614e64e-d981-4eba-b016-d9822f09a4fb",
                                                                  "name": "AOL"},
                         'f1a5e99c-8edf-489a-9c72-6cabe6c387fc': {"id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
                                                                  "name": "Apple"},
                         '7fc0e8ab-189c-4794-b8f4-9f05a1db185b': {"id": "7fc0e8ab-189c-4794-b8f4-9f05a1db185b",
                                                                  "name": "Apricot"},
                         '0a6018a0-3e67-4407-b120-780932434b36': {"id": "0a6018a0-3e67-4407-b120-780932434b36",
                                                                  "name": "Asparagus"},
                         '3b136c4b-7a14-4904-9e01-13364dd7b973': {"ru_id": "3b136c4b-7a14-4904-9e01-13364dd7b973",
                                                                  "business_name": "Bolts & Ratchet Ltd"},
                         'b3ba864b-7cbc-4f44-84fe-88dc018a1a4c': {
                                                                 "associations": [
                                                                     {
                                                                         "enrolments": [
                                                                             {
                                                                                 "enrolmentStatus": "ENABLED",
                                                                                 "name": "Business Register and Employment Survey",
                                                                                 "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                                                                             }
                                                                         ],
                                                                         "partyId": "cd592e0f-8d07-407b-b75d-e01fbdae8233"
                                                                     }
                                                                 ],
                                                                 "ruref": "50012345678",
                                                                 "checkletter": "A",
                                                                 "frosic92": "11111",
                                                                 "rusic92": "11111",
                                                                 "frosic2007": "11111",
                                                                 "rusic2007": "11111",
                                                                 "froempment": 50,
                                                                 "frotover": 50,
                                                                 "entref": "1234567890",
                                                                 "legalstatus": "B",
                                                                 "entrepmkr": "C",
                                                                 "region": "DE",
                                                                 "birthdate": "01/09/1993",
                                                                 "entname1": "ENTNAME1",
                                                                 "entname2": "ENTNAME2",
                                                                 "entname3": "ENTNAME3",
                                                                 "runame1": "Bolts",
                                                                 "runame2": "and",
                                                                 "runame3": "Ratchets Ltd",
                                                                 "tradstyle1": "TRADSTYLE1",
                                                                 "tradstyle2": "TRADSTYLE2",
                                                                 "tradstyle3": "TRADSTYLE3",
                                                                 "seltype": "F",
                                                                 "inclexcl": "G",
                                                                 "cell_no": 1,
                                                                 "formtype": "0001",
                                                                 "currency": "H",
                                                                 "name": "Bolts and Ratchets Ltd",
                                                                 "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
                                                                 "sampleUnitRef": "50012345678",
                                                                 "sampleUnitType": "B"
                                                             }
                         }

    _respondent_ids = {'f62dfda8-73b0-4e0e-97cf-1b06327a6712': {"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712",
                                                                "firstName": "Bhavana",
                                                                "lastName": "Lincoln",
                                                                "emailAddress": "lincoln.bhavana@gmail.com",
                                                                "telephone": "+443069990888",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       'ce12b958-2a5f-44f4-a6da-861e59070a31': {"id": "ce12b958-2a5f-44f4-a6da-861e59070a31",
                                                                "firstName": "Lars",
                                                                "lastName": "McEachern",
                                                                "emailAddress": "mclars@yahoo.com",
                                                                "telephone": "+443069990413",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       '0a7ad740-10d5-4ecb-b7ca-3c0384afb882': {"id": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882",
                                                                "firstName": "Vana",
                                                                "lastName": "Oorschot",
                                                                "emailAddress": "vana123@aol.com",
                                                                "telephone": "+443069990289",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       '01b51fcc-ed43-4cdb-ad1c-450f9986859b': {"id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
                                                                "firstName": "Chandana",
                                                                "lastName": "Blanchet",
                                                                "emailAddress": "cblanc@hotmail.co.uk",
                                                                "telephone": "+443069990854",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       'dd5a38ff-1ecb-4634-94c8-2358df33e614': {"id": "dd5a38ff-1ecb-4634-94c8-2358df33e614",
                                                                "firstName": "Ida",
                                                                "lastName": "Larue",
                                                                "emailAddress": "ilarue47@yopmail.com",
                                                                "telephone": "+443069990250",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       constants.BRES_USER:                     {"id": "BRES",
                                                                 "firstName": "BRES",
                                                                 "lastName": "",
                                                                 "emailAddress": "",
                                                                 "telephone": "",
                                                                 "status": "",
                                                                 "sampleUnitType": "BI"},
                       'AnotherSurvey':                        {"id": "AnotherSurvey",
                                                                "firstName": "AnotherSurvey",
                                                                "lastName": "",
                                                                "emailAddress": "",
                                                                "telephone": "",
                                                                "status": "",
                                                                "sampleUnitType": "BI"},
                       'ce12b958-2a5f-44f4-a6da-861e59070a32': {"id": "ce12b958-2a5f-44f4-a6da-861e59070a32",
                                                                "firstName": "Liz",
                                                                "lastName": "Larkin",
                                                                "emailAddress": "ilarue47@yopmail.com",
                                                                "telephone": "+443069990250",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       'db036fd7-ce17-40c2-a8fc-932e7c228397': {"id": "db036fd7-ce17-40c2-a8fc-932e7c228397",
                                                                "firstName": "Peter",
                                                                "lastName": "Smith",
                                                                "emailAddress": "peter.smith@hostmail.com",
                                                                "telephone": "+447894056785",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       'ab123456-ce17-40c2-a8fc-abcdef123456': {"associations": [
                                                                                   {"enrolments": [{
                                                                                       "enrolmentStatus": "ENABLED",
                                                                                       "name": "Business Register and Employment Survey",
                                                                                       "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                                                                                       }],
                                                                                       "partyId": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
                                                                                       "sampleUnitRef": "50012345678"
                                                                                   }
                                                                               ],
                                                                "id": "ab123456-ce17-40c2-a8fc-abcdef123456",
                                                                "firstName": "Ivor",
                                                                "lastName": "Bres",
                                                                "emailAddress": "ivor.bres@hostmail.com",
                                                                "telephone": "+447894056785",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"},
                       '654321ab-ce17-40c2-a8fc-abcdef123456': {"associations": [
                                                                                   {"enrolments": [],
                                                                                    "partyId": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
                                                                                    "sampleUnitRef": "50012345678"
                                                                                    }
                                                                               ],
                                                                "id": "654321ab-ce17-40c2-a8fc-abcdef123456",
                                                                "firstName": "IvorNot",
                                                                "lastName": "Bres",
                                                                "emailAddress": "ivorNot.bres@hostmail.com",
                                                                "telephone": "+447894056786",
                                                                "status": "ACTIVE",
                                                                "sampleUnitType": "BI"}
                       }


