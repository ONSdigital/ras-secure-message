# Secure Messaging API


* `GET /messages`

&mdash; When a list of messages is requested this returns a generic representation of the list of messages available.

&mdash; Results can be filtered further by using query parameters:

| `**Variable**` | `**Type**` | `**Example Value**` |
| :---: | :---: | :---: |
| cc (collection_case) | `string` | ACollectionCase |
| ru_id | `string` | (not implemented)
| survey | `string` | BRES |
| label | `string` | INBOX/DRAFT/SENT |
| ce (collection_exercise) | `string`| ACollectionExercise |
| desc (descending) | `boolean` | True/False
| limit | `int` | 2 |

   * An example of using one the above would be: `GET /messages?limit=2` 
   * Using multiple parameters: `GET /messages?limit=2&label=INBOX`

### Example JSON Response

```json
{
    "_links": {
        "first": {
            "href": "http://localhost:5050/messages"
        },
        "next": {
            "href": "http://localhost:5050/messages?page=2&limit=20"
        },
        "self": {
            "href": "http://localhost:5050/messages?page=1&limit=20"
        }
    },
    "messages": [
        {
            "@msg_from": {
                "emailAddress": "",
                "firstName": "BRES",
                "id": "BRES",
                "lastName": "",
                "sampleUnitType": "BI",
                "status": "",
                "telephone": ""
            },
            "@msg_to": [
                {
                    "associations": [
                        {
                            "enrolments": [
                                {
                                    "enrolmentStatus": "ENABLED",
                                    "name": "Survey Name",
                                    "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                                }
                            ],
                            "partyId": "1f5e1d68-2a4c-4698-8086-e23c0b98923f",
                            "sampleUnitRef": "50012345678"
                        }
                    ],
                    "emailAddress": "name@email.co.uk",
                    "firstName": "FirstName",
                    "id": "ef7737df-2097-4a73-a530-e98dba7bf28f",
                    "lastName": "LastName",
                    "sampleUnitType": "BI",
                    "status": "ACTIVE",
                    "telephone": "07832323234"
                }
            ],
            "@ru_id": null,
            "_links": {
                "self": {
                    "href": "http://localhost:5050/message/ae46748b-c6e6-4859-a57a-86e01db2dcbc"
                }
            },
            "body": "Test uuid",
            "collection_case": "ACollectionCase",
            "collection_exercise": "",
            "labels": [
                "DRAFT"
            ],
            "modified_date": "2017-10-03 15:51:32.961321",
            "msg_from": "BRES",
            "msg_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc",
            "msg_to": [
                "ef7737df-2097-4a73-a530-e98dba7bf28f"
            ],
            "ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "subject": "Test uuid",
            "survey": "BRES",
            "thread_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc"
        }
]}
```

* `POST /message/send`

### Example JSON DATA for post

```json
{
  "msg_to": ["ef7737df-2097-4a73-a530-e98dba7bf28f"],
  "msg_from": "BRES",
  "subject": "Test uuid",
  "body": "Test uuid",
  "thread_id": "",
  "ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
  "collection_case": "ACollectionCase",
  "survey": "BRES" 
}
```

### Example JSON Response

```json
{
    "msg_id": "f0bf34fd-f5bd-4a17-a641-7ad976fef140",
    "status": "201",
    "thread_id": "f0bf34fd-f5bd-4a17-a641-7ad976fef140"
}
```

* `GET /message/{id}`

&mdash; When an individual message is requested by message id, it returns the specific message by the message id.

### Example JSON Response

```json
{ "@msg_from": {
        "emailAddress": "",
        "firstName": "BRES",
        "id": "BRES",
        "lastName": "",
        "sampleUnitType": "BI",
        "status": "",
        "telephone": ""
    },
    "@msg_to": [
        {
            "associations": [
                {
                    "enrolments": [
                        {
                            "enrolmentStatus": "ENABLED",
                            "name": "Survey Name",
                            "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                        }
                    ],
                    "partyId": "86b7a550-0f22-444a-be3c-9824b0ad5450",
                    "sampleUnitRef": "50012345678"
                }
            ],
            "emailAddress": "name@email.co.uk",
            "firstName": "FirstName",
            "id": "a0e833fe-8a2d-4293-903b-4b826732e079",
            "lastName": "LastName",
            "sampleUnitType": "BI",
            "status": "ACTIVE",
            "telephone": "07832323234"
        }
    ],
    "@ru_id": null,
    "_links": "",
    "body": "Test internal message",
    "collection_case": "ACollectionCase",
    "collection_exercise": "",
    "labels": [
        "SENT"
    ],
    "msg_from": "BRES",
    "msg_id": "5a43b35d-0b28-4b60-9070-4f27e799b280",
    "msg_to": [
        "a0e833fe-8a2d-4293-903b-4b826732e079"
    ]
    }
```

* `PUT message/{id}/modify`

### Example JSON DATA for put

```json
{
"action" : "add",
"label" : "UNREAD"
}
```

### Example JSON Response

```json
{
    "status": "ok"
}
```

* `GET /drafts`

### Example JSON Response

```json
{
    "_links": {
        "first": {
            "href": "http://localhost:5050/drafts"
        },
        "self": {
            "href": "http://localhost:5050/drafts?page=1&limit=20"
        }
    },
    "messages": [
        {
            "@msg_from": {
                "emailAddress": "",
                "firstName": "BRES",
                "id": "BRES",
                "lastName": "",
                "sampleUnitType": "BI",
                "status": "",
                "telephone": ""
            },
            "@msg_to": [
                {
                    "associations": [
                        {
                            "enrolments": [
                                {
                                    "enrolmentStatus": "ENABLED",
                                    "name": "Survey Name",
                                    "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                                }
                            ],
                            "partyId": "1f5e1d68-2a4c-4698-8086-e23c0b98923f",
                            "sampleUnitRef": "50012345678"
                        }
                    ],
                    "emailAddress": "name@email.co.uk",
                    "firstName": "FirstName",
                    "id": "ef7737df-2097-4a73-a530-e98dba7bf28f",
                    "lastName": "LastName",
                    "sampleUnitType": "BI",
                    "status": "ACTIVE",
                    "telephone": "07832323234"
                }
            ],
            "@ru_id": null,
            "_links": {
                "self": {
                    "href": "http://localhost:5050/message/ae46748b-c6e6-4859-a57a-86e01db2dcbc"
                }
            },
            "body": "Test uuid",
            "collection_case": "ACollectionCase",
            "collection_exercise": "",
            "labels": [
                "DRAFT"
            ],
            "modified_date": "2017-10-03 15:51:32.961321",
            "msg_from": "BRES",
            "msg_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc",
            "msg_to": [
                "ef7737df-2097-4a73-a530-e98dba7bf28f"
            ],
            "ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "subject": "Test uuid",
            "survey": "BRES",
            "thread_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc"
        }
    ]
}
```

* `POST /draft/save`

### Example JSON DATA for post

```json
{
  "msg_to": ["ef7737df-2097-4a73-a530-e98dba7bf28f"],
  "msg_from": "BRES",
  "subject": "Test uuid",
  "body": "Save message",
  "thread_id": "",
  "ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
  "collection_case": "ACollectionCase",
  "survey": "BRES" 
}
```

### Example JSON Response

```json
{
    "msg_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc",
    "status": "OK",
    "thread_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc"
}
```

* `GET /draft/{id}`

### Example JSON Response

```json
{
    "@msg_from": {
        "emailAddress": "",
        "firstName": "BRES",
        "id": "BRES",
        "lastName": "",
        "sampleUnitType": "BI",
        "status": "",
        "telephone": ""
    },
    "@msg_to": [
        {
            "associations": [
                {
                    "enrolments": [
                        {
                            "enrolmentStatus": "ENABLED",
                            "name": "Survey Name",
                            "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                        }
                    ],
                    "partyId": "1f5e1d68-2a4c-4698-8086-e23c0b98923f",
                    "sampleUnitRef": "50012345678"
                }
            ],
            "emailAddress": "name@email.co.uk",
            "firstName": "FirstName",
            "id": "ef7737df-2097-4a73-a530-e98dba7bf28f",
            "lastName": "LastName",
            "sampleUnitType": "BI",
            "status": "ACTIVE",
            "telephone": "07832323234"
        }
    ],
    "@ru_id": null,
    "_links": "",
    "body": "Test uuid",
    "collection_case": "ACollectionCase",
    "collection_exercise": "",
    "labels": [
        "DRAFT"
    ],
    "modified_date": "2017-10-03 15:51:32.961321",
    "msg_from": "BRES",
    "msg_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc",
    "msg_to": [
        "ef7737df-2097-4a73-a530-e98dba7bf28f"
    ],
    "ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
    "subject": "Test uuid",
    "survey": "BRES",
    "thread_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc"
}
```

* `PUT /draft/{id}/modify`

### Example JSON DATA for put

```json
{
  "msg_to": ["ef7737df-2097-4a73-a530-e98dba7bf28f"],
  "msg_id": "30c68b01-7aff-49a9-9bb8-cd78c68ffb74",
  "msg_from": "BRES",
  "subject": "Test uuid",
  "body": "Save message",
  "thread_id": "",
  "ru_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
  "collection_case": "ACollectionCase",
  "survey": "BRES" 
}
```

### Example JSON Response

```json
{
    "msg_id": "30c68b01-7aff-49a9-9bb8-cd78c68ffb74",
    "status": "OK"
}
```

* `GET /labels?name=unread`

### Example JSON Response

```json
{
    "name": "unread",
    "total": 39
}
```
