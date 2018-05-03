import requests
import json

for x in range(0, 50):
    print(f"Sending message {x}")
    subject = f"{x} subject"
    body = f"{x} body"

    message = {
      "msg_to": ["87f6afc9-d330-4eee-8b39-6841eb6a7d8a"],
      "msg_from": "a5c6a83d-583f-4ccb-9e84-13db14aa7b3f",
      "subject": subject,
      "body": body,
      "thread_id": "",
      "ru_id": "bc18424f-7f1b-4877-b6e0-94cd5d928559",
      "collection_case": "",
      "survey": "02b9c366-7397-42f7-942a-76dc5876d86d"
    }
    requests.post("http://localhost:5050/v2/messages", headers={'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXJ0eV9pZCI6ImE1YzZhODNkLTU4M2YtNGNjYi05ZTg0LTEzZGIxNGFhN2IzZiIsInJvbGUiOiJpbnRlcm5hbCJ9.SuEpUCZwY7b6gRMOF6FTOB09O82EXRrI-7nhRogNnaw', 'Content-Type': 'application/json',
                                   'Accept': 'application/json'}, data=json.dumps(message))
