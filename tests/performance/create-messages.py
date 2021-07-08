import json

from requests import HTTPError, post

for x in range(0, 50):
    print(f"Sending message {x}")
    subject = f"{x} subject"
    body = f"{x} body"

    message = {
        "msg_to": ["6097fcae-6ce3-4212-9d72-6189b715be24"],
        "msg_from": "e359bb85-13e1-48df-b012-aa14e26b00d6",
        "subject": subject,
        "body": body,
        "thread_id": "",
        "business_id": "47e5859b-5d18-4c73-a91c-05491f6c6167",
        "case_id": "",
        "survey_id": "02b9c366-7397-42f7-942a-76dc5876d86d",
    }
    response = post(
        "http://localhost:5050/messages",
        headers={
            "Authorization": "<insert jwt here>",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        data=json.dumps(message),
    )

    try:
        response.raise_for_status()
        print(f"Message {x} sucessfully sent")
    except HTTPError:
        print(f"Message {x} failed to send")
