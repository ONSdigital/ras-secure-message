
respondent_ids = {}

respondent_ids['f62dfda8-73b0-4e0e-97cf-1b06327a6712'] = {"firstname": "Bhavana", "surname": "Lincoln", "telephone": "+443069990888", "status": "ACTIVE"}
respondent_ids['b28c8a88-5476-4dc0-b91a-831fdbecb8b8'] = {"firstname": "Lars", "surname": "McEachern", "telephone": "+443069990413", "status": "ACTIVE"}
respondent_ids['a3d276b6-39b4-4dfa-8034-384a08b56b34'] = {"firstname": "Vana", "surname": "Oorschot", "telephone": "+443069990289", "status": "ACTIVE"}
respondent_ids['01b51fcc-ed43-4cdb-ad1c-450f9986859b'] = {"firstname": "Chandana", "surname": "Blanchet", "telephone": "+443069990854", "status": "ACTIVE"}
respondent_ids['dd5a38ff-1ecb-4634-94c8-2358df33e614'] = {"firstname": "Ida", "surname": "Larue", "telephone": "+443069990250", "status": "ACTIVE"}


def get_details_by_uuid(uuid):
    respondent_details = {}
    for x in uuid:
        respondent_details[x] = respondent_ids[x]
    return respondent_details


