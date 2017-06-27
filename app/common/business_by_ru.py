from werkzeug.exceptions import BadRequest

business_details = {}

business_details['c614e64e-d981-4eba-b016-d9822f09a4fb'] = {"ru_ref": "c614e64e-d981-4eba-b016-d9822f09a4fb", "business_name": "AOL"}
business_details['f1a5e99c-8edf-489a-9c72-6cabe6c387fc'] = {"ru_ref": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc", "business_name": "Apple"}
business_details['7fc0e8ab-189c-4794-b8f4-9f05a1db185b'] = {"ru_ref": "7fc0e8ab-189c-4794-b8f4-9f05a1db185b", "business_name": "Apricot"}
business_details['0a6018a0-3e67-4407-b120-780932434b36'] = {"ru_ref": "0a6018a0-3e67-4407-b120-780932434b36", "business_name": "Asparagus"}


def get_business_details_by_ru(rus):
    details = []

    for x in rus:
        try:
            details.append(business_details[x])
        except KeyError:
            raise (BadRequest(description="An issue with RU"))
    return details
