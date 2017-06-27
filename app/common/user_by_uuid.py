from werkzeug.exceptions import BadRequest

respondent_ids = {}

respondent_ids['f62dfda8-73b0-4e0e-97cf-1b06327a6712'] = {"id": "f62dfda8-73b0-4e0e-97cf-1b06327a6712", "firstname": "Bhavana", "surname": "Lincoln", "email": "lincoln.bhavana@gmail.com", "telephone": "+443069990888", "status": "ACTIVE"}
respondent_ids['ce12b958-2a5f-44f4-a6da-861e59070a31'] = {"id": "ce12b958-2a5f-44f4-a6da-861e59070a31", "firstname": "Lars", "surname": "McEachern", "email": "mclars@yahoo.com", "telephone": "+443069990413", "status": "ACTIVE"}
respondent_ids['0a7ad740-10d5-4ecb-b7ca-3c0384afb882'] = {"id": "0a7ad740-10d5-4ecb-b7ca-3c0384afb882", "firstname": "Vana", "surname": "Oorschot", "email": "vana123@aol.com", "telephone": "+443069990289", "status": "ACTIVE"}
respondent_ids['01b51fcc-ed43-4cdb-ad1c-450f9986859b'] = {"id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b", "firstname": "Chandana", "surname": "Blanchet", "email": "cblanc@hotmail.co.uk", "telephone": "+443069990854", "status": "ACTIVE"}
respondent_ids['dd5a38ff-1ecb-4634-94c8-2358df33e614'] = {"id": "dd5a38ff-1ecb-4634-94c8-2358df33e614", "firstname": "Ida", "surname": "Larue", "email": "ilarue47@yopmail.com", "telephone": "+443069990250", "status": "ACTIVE"}
respondent_ids['BRES'] = {"id": "BRES", "firstname": "BRES", "surname": "", "email": "", "telephone": "", "status": ""}
respondent_ids['AnotherSurvey'] = {"id": "AnotherSurvey", "firstname": "AnotherSurvey", "surname": "", "email": "", "telephone": "", "status": ""}


def get_details_by_uuids(uuids):
        respondent_details = []
        for x in uuids:
            try:
                respondent_details.append(respondent_ids[x])
            except KeyError:
                raise (BadRequest(description="An error has occurred"))
        return respondent_details
