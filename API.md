# Secure Messaging API

## Contents

* [Overview](#overview)
* [Message Fields](#message-fields)
* [JWT](#jwt)
* Messages
  * [Get Message List](#get-message-list)
  * [Send Message](#send-message)
  * [Modify Message Labels](#modify-message-labels)
* Conversations
  * [Get conversation list](#get-conversation-list)
  * [Get conversation list](#get-conversation-list)
  * [Get conversations count](#get-conversations-count)
  * [Patch Conversation Metadata](#patch-conversation-metadata)
* Health and Status
  * [Get Health](#get-health)
  * [Get Health With Database-status](#get-health-with-database-status)
  * [Get Service Details](#get-service-details)
  * [Get Service Version](#get-service-version)

## Overview

The secure message service provides a method by which messages may be passed between an enrolled respondent and the ONS.

The 'secure' aspect alludes to it not being email , it uses a message store in a database within the ONS. So that the only time 'messages' leave is to be rendered on a web page.

Messages are sent using an email-like set of characteristics (From, To, Subject and Body). They also encompass ONS specific meta data such as survey, collection case, reporting unit and collection instrument.

The api uses UUIDs to define from, to, survey, collection case, reporting unit and collection exercise.

Each message is stored internally with a set of flags that indicate the state of the message per actor. These flags are known as labels in the service. That is if person A sends a message to person B then person A will have a label of SENT and person B will have a labels of INBOX and UNREAD. This storage of state per actor is crucial.

The api endpoints fall into 4 groups:

* Messages - These end points can be used to send a message , read a message, get a count of unread messages , and change a label on a message
* Conversations - Messages can exist as part of a conversation. Messages within a conversation share the same thread identifier. Conversations/Threads can be obtained via a list of conversations or a specific conversation.
* Health and Information - Several endpoints are provided that can be used to view the health and status of the service

### Message Fields

See the endpoint descriptions for detailed usage of each field. This is an overview.

* Message id . (msg_id) This is an id assigned to a message when it is created . It is a uuid. Some endpoints expect a message id whilst others will error if a message id is presented.See each endpoint for details.
* Thread id . (thread_id) This is a unique identifier for a conversation. If a thread id is presented on message post then the api will assume that a message is part of an existing conversation.
* From . (msg_from) This is the uuid of the actor that sent a message. If the actor is a respondent then it is their user uuid. If they are an internal user then it will be their user uuid.
* To . (msg_to) These are the user uuids of the recipients of the message. Currently only one to user is supported. The message to can be as 'From' but with the addition that it can be the constant 'GROUP' to indicate that the message is being sent to a group handling the specific survey at the ons.
* Subject . (subject) The subject of the message. Limited in the API to 100 characters , but since replies are prefixed with 'Re: ' then in practice it is 96 characters.
* Body . (body) Up to 10000 characters.
* Survey . (survey). This is the uuid of the survey . It is mandatory when saving a message.
* Collection Exercise .  (collection exercise) uuid of the collection exercise , can be used as a filter option (ce)
* Reporting unit . (ru) uuid of the reporting unit . Can be used as a filter option.
* Labels . These can be used to set a status on a message, or retrieve messages with a specific label. Valid labels:
  * SENT  Added to a message for the actor who sent the message
  * INBOX Added to the message for the actor who received the message
  * UNREAD Added to a message to indicate that a message has not been read
* page . Which page of the result set is to be returned when getting a list of messages/threads
* limit . How many messages to return per page when getting a list of messages/threads.

## JWT

All calls , except health , health details and info , require that a valid JWT be passed in an Authorization header.
this currently has two fields:

* party_id which is how the user is identified, this should be the users uuid
* role which is set to either 'internal' for ons staff or 'respondent' for respondents.

The algorithm and secret are defined in the configuration file. If the algorithm and/or secret are out of step between client and secure message service then the JWT will fail checks and the service will return a 500.

Being able to get a response from a health or info endpoint but 500's from a message post or read is often an indicator that something in this area is not configured correctly. An easy check for config is to access the /health/details endpoint.

## Get Message List

`GET /messages`

Retrieves a list of messages based on the selected parameters passed on the query string.

&mdash; When a list of messages is requested this returns a generic representation of the list of messages available.

&mdash; Results can be filtered further by using query parameters:

| `**Variable**` | `**Type**` | `**Example Value**` | `**Notes**` |
| :---: | :---: | :---: | :---: |
| cc (collection_case) | `string` | 0000000000000000 | optionally restrict by collection case |
| business_id | `string` | aaa1aa1a-1aa1-1111-aa11-11a11aa111aa | optionally restrict by ru id  |
| survey | `string` | aaa1aa1a-1aa1-1111-aa11-11a11aa111aa | optionally restrict by survey  |
| label | `string` | INBOX/SENT | used to select types of messages to return e.g SENT or INBOX |
| ce (collection_exercise) | `string`| aaa1aa1a-1aa1-1111-aa11-11a11aa111aa | optionally restrict by collection exercise |
| desc (descending) | `boolean` | True/False | order by date descending (else ascending) |
| limit | `int` | 2 | maximum number of messages to return per page |
| page  | 'int' | 1 | which page of data to return |

* An example of using one the above would be: `GET /messages?limit=2`
* Using multiple parameters: `GET /messages?limit=2&label=INBOX&survey=12345678981047653839`

Note that if the user is a respondent the get messages returns messages which match the uuid of the user passed in the JWT and that satisfy any additional filter criteria. If the user is internal then it matches messages sent to all internal users that satisfy the additional filter criteria . Typically that would be restricted by survey_id so that only messages  of a specific survey are returned.

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
            "@business_details": null,
            "_links": {
                "self": {
                    "href": "http://localhost:5050/message/ae46748b-c6e6-4859-a57a-86e01db2dcbc"
                }
            },
            "body": "Test uuid",
            "collection_case": "ACollectionCase",
            "collection_exercise": "",
            "labels": [
                "INBOX"
            ],
            "modified_date": "2017-10-03 15:51:32.961321",
            "msg_from": "BRES",
            "msg_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc",
            "msg_to": [
                "ef7737df-2097-4a73-a530-e98dba7bf28f"
            ],
            "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
            "subject": "Test uuid",
            "survey": "BRES",
            "thread_id": "ae46748b-c6e6-4859-a57a-86e01db2dcbc"
        }
]}
```

Note the message response contains @msg_from , @msg_to and @business_details . These hold values that the secure message api has resolved from the party service or the user authentication service. They are not guaranteed to be populated if the service is not available or if the message was sent to 'GROUP'

## Send Message

`POST /messages`

The messages post endpoint stores a secure message . If the recipient is a respondent it will also send an email via Notify.Gov.

Note, the message post must have a Content-Type header of `application/json` , else it will return an error.

When a message is posted, typically, no msg_id is supplied.

### Example JSON DATA for post Version 1

```json
{
  "msg_to": ["ef7737df-2097-4a73-a530-e98dba7bf28f"],
  "msg_from": "BRES",
  "subject": "Test uuid",
  "body": "Test uuid",
  "thread_id": "",
  "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
  "collection_case": "ACollectionCase",
  "survey": "BRES"
}
```

### Example JSON DATA for post Version 2

* msg_to - Should be set to a specific user uuid if known , else to the constant 'GROUP' if sending to an unknown user in ONS
* msg_from - The current user uuid
* thread_id - Should be set to the thread id of the message being replied to if the message is a reply, else left empty
* survey - Should be the uuid of the survey.
* collection_case - The uuid of the collection case. Can be used as a filter option (cc).

```json
{
  "msg_to": ["ef7737df-2097-4a73-a530-e98dba7bf28f"],
  "msg_from": "d45e99c-8edf-489a-9c72-6cabe6c387fc",
  "subject": "Test uuid",
  "body": "Test uuid",
  "thread_id": "",
  "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
  "collection_case": "ACollectionCase",
  "survey": "2346e99c-8edf-489a-9c72-6cabe6c387fc"
}
```

### Example JSON Response version 1 and 2

Note if the message is a new message ( not a reply to an existing one) then the thread_id and the message_id will be the same. This indicates that this message is the first in a conversation. Subsequent messages in a conversation will have their own msg_id but all share the same thread_id

```json
{
    "msg_id": "f0bf34fd-f5bd-4a17-a641-7ad976fef140",
    "status": "201",
    "thread_id": "f0bf34fd-f5bd-4a17-a641-7ad976fef140"
}
```

## Modify Message Labels

`PUT /messages/modify/<message_id>`  

This is used to modify the labels (aka status) associated with a message.
Currently only limited label names and actions are supported. It is typically used to mark a message as read/unread.

`UNREAD` is the only valid label name. Other labels will result in errors.
Valid actions : `add`,`remove` . Other actions will result in errors.

Note there is only an UNREAD label , absence of `UNREAD` is interpreted as the message has been read

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

## Get Conversation list

`GET /threads`

This returns the latest message in each conversation(aka thread) that satisfies the passed in
criteria.
It can use the same filter arguments as Get Messages, and returns the latest message in each thread that satisfies
the criteria passed in [Get Message List](#get-message-list)

Additional parameters above those on Get Message List:  

* is_closed           If set and value = 'true' then only returns conversations that have been marked as closed, else returns open conversations
* my_conversations    If set and value ='true' then for an internal user will only retrieve conversations where they were an actor in the
latest message on the thread. I.e they sent the message or it was sent specifically to them. If set true when the user is a respondent then it returns a 400

### Example JSON Response

Note, the response will have either uuids or 'GROUP' for the user ids, and a uuid for the survey id

```json
{
  "_links": {
    "first": {
      "href": "http://localhost:5050/threads"
    },
    "self": {
      "href": "http://localhost:5050/threads?page=1&limit=20"
    }
  },
  "messages": [
    {
      "@msg_from": {
        "emailAddress": "cblanc@hotmail.co.uk",
        "firstName": "Chandana",
        "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
        "lastName": "Blanchet",
        "sampleUnitType": "BI",
        "status": "ACTIVE",
        "telephone": "+443069990854"
      },
      "@msg_to": [
        {
          "emailAddress": "mock@email.com",
          "firstName": "BRES",
          "id": "BRES",
          "lastName": ""
        }
      ],
      "@business_details": {
        "id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
        "name": "Apple"
      },
      "_links": {
        "self": {
          "href": "http://localhost:5050/message/8966ecec-c77d-413e-993c-9bdb44b62b86"
        }
      },
      "body": "Test",
      "collection_case": "collection case1",
      "collection_exercise": "collection exercise1",
      "from_internal": "False",
      "labels": [
        "SENT"
      ],
      "msg_from": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
      "msg_id": "8966ecec-c77d-413e-993c-9bdb44b62b86",
      "msg_to": [
        "BRES"
      ],
      "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
      "sent_date": "2018-02-22 14:54:25.637222",
      "subject": "Hello World",
      "survey": "33333333-22222-3333-4444-88dc018a1a4c",
      "thread_id": "8966ecec-c77d-413e-993c-9bdb44b62b86"
    },
    {
      "@msg_from": {
        "emailAddress": "cblanc@hotmail.co.uk",
        "firstName": "Chandana",
        "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
        "lastName": "Blanchet",
        "sampleUnitType": "BI",
        "status": "ACTIVE",
        "telephone": "+443069990854"
      },
      "@msg_to": [
        {
          "emailAddress": "mock@email.com",
          "firstName": "BRES",
          "id": "BRES",
          "lastName": ""
        }
      ],
      "@business_details": {
        "id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
        "name": "Apple"
      },
      "_links": {
        "self": {
          "href": "http://localhost:5050/message/a55ac787-caae-4678-a4a7-a91dc9463b16"
        }
      },
      "body": "Test",
      "collection_case": "collection case1",
      "collection_exercise": "collection exercise1",
      "from_internal": "False",
      "labels": [
        "SENT"
      ],
      "msg_from": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
      "msg_id": "a55ac787-caae-4678-a4a7-a91dc9463b16",
      "msg_to": [
        "BRES"
      ],
      "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
      "sent_date": "2018-02-22 14:54:25.616215",
      "subject": "Hello World",
      "survey": "33333333-22222-3333-4444-88dc018a1a4c",
      "thread_id": "a55ac787-caae-4678-a4a7-a91dc9463b16"
    },
    {
      "@msg_from": {
        "emailAddress": "cblanc@hotmail.co.uk",
        "firstName": "Chandana",
        "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
        "lastName": "Blanchet",
        "sampleUnitType": "BI",
        "status": "ACTIVE",
        "telephone": "+443069990854"
      },
      "@msg_to": [
        {
          "emailAddress": "mock@email.com",
          "firstName": "BRES",
          "id": "BRES",
          "lastName": ""
        }
      ],
      "@business_details": {
        "id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
        "name": "Apple"
      },
      "_links": {
        "self": {
          "href": "http://localhost:5050/message/16e5b6c5-37d4-41ee-b9d3-9b8eb0b75245"
        }
      },
      "body": "Test",
      "collection_case": "collection case1",
      "collection_exercise": "collection exercise1",
      "from_internal": "False",
      "labels": [
        "SENT"
      ],
      "msg_from": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
      "msg_id": "16e5b6c5-37d4-41ee-b9d3-9b8eb0b75245",
      "msg_to": [
        "BRES"
      ],
      "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
      "sent_date": "2018-02-22 14:54:25.576722",
      "subject": "Hello World",
      "survey": "33333333-22222-3333-4444-88dc018a1a4c",
      "thread_id": "16e5b6c5-37d4-41ee-b9d3-9b8eb0b75245"
    }
  ]
}
```

For descriptions of @msg_from, @msg_to and @business_details see messages get
[Get Message List](#get-message-list)

## Get Conversations count  

`GET /messages/count`

This returns a count of the conversations that satisfy the search criteria.
Available search criteria matches those on get threads:

* survey - If set then only conversations regarding this survey will be considered. Defaults to all surveys
* is_closed - If set true then only closed conversations will be considered. Defaults to false if omitted.
* my_conversations - If set true then will only return conversations where the currently signed in user is an actor in the last message of the conversation.
* new_respondent_conversations - If set true then only counts new conversations by the respondent. I.e ones not replied to
* all_conversation_types - If set true will override is_closed, my_conversations and new_respondent_conversations
  in the count end point, and return 4 counts for open, close, my_conversations and new_respondent_conversations.
  Slower than asking for a specific conversation type so only use where all 4 counts are needed. 
  Use specific counts if they suffice.
* business_id - If set then restrict conversations to those regarding a specific ru
* cc - If set then restricts the conversations to a specific collection case
* ce - If set then restricts the conversations to a specific collction exercise

### Example JSON Response

```json
{
  "total":14
}

```

## Get Conversation by Id

`GET /threads/<thread_id>`

This has been implemented but not used in production, hence should be treated with caution.
This returns all messages on a specific thread.

Note there is a known bug here. That is messages are ordered by date of entry which may not be correct if several
sub conversations are in progress (i.e two internal users replying on a thread ).

### Example JSON Response

Messages should have survey_id, collection_case and use either a uuid or "GROUP" for the internal user.

```json
{
  "_links": {
    "first": {
      "href": "http://localhost:5050/threads/78e3caa6-2e27-4ad3-bd38-168b2cc3ef5d"
    },
    "self": {
      "href": "http://localhost:5050/threads/78e3caa6-2e27-4ad3-bd38-168b2cc3ef5d?page=1&limit=20"
    }
  },
  "messages": [
    {
      "@msg_from": {
        "emailAddress": "cblanc@hotmail.co.uk",
        "firstName": "Chandana",
        "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
        "lastName": "Blanchet",
        "sampleUnitType": "BI",
        "status": "ACTIVE",
        "telephone": "+443069990854"
      },
      "@msg_to": [
        {
          "emailAddress": "mock@email.com",
          "firstName": "BRES",
          "id": "BRES",
          "lastName": ""
        }
      ],
      "@business_details": {
        "id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
        "name": "Apple"
      },
      "_links": {
        "self": {
          "href": "http://localhost:5050/message/c3b0418e-d723-41e9-9a89-4bacac6e8f0b"
        }
      },
      "body": "Test",
      "collection_case": "collection case1",
      "collection_exercise": "collection exercise1",
      "from_internal": "False",
      "labels": [
        "SENT"
      ],
      "msg_from": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
      "msg_id": "c3b0418e-d723-41e9-9a89-4bacac6e8f0b",
      "msg_to": [
        "BRES"
      ],
      "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
      "sent_date": "2018-02-22 15:02:07.230759",
      "subject": "Hello World",
      "survey": "33333333-22222-3333-4444-88dc018a1a4c",
      "thread_id": "78e3caa6-2e27-4ad3-bd38-168b2cc3ef5d"
    },
    {
      "@msg_from": {
        "emailAddress": "mock@email.com",
        "firstName": "BRES",
        "id": "BRES",
        "lastName": ""
      },
      "@msg_to": [
        {
          "emailAddress": "cblanc@hotmail.co.uk",
          "firstName": "Chandana",
          "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
          "lastName": "Blanchet",
          "sampleUnitType": "BI",
          "status": "ACTIVE",
          "telephone": "+443069990854"
        }
      ],
      "@business_details": {
        "id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
        "name": "Apple"
      },
      "_links": {
        "self": {
          "href": "http://localhost:5050/message/1238dfa6-24e5-46d0-9992-338637080672"
        }
      },
      "body": "Test",
      "collection_case": "collection case1",
      "collection_exercise": "collection exercise1",
      "from_internal": "True",
      "labels": [
        "INBOX",
        "UNREAD"
      ],
      "msg_from": "BRES",
      "msg_id": "1238dfa6-24e5-46d0-9992-338637080672",
      "msg_to": [
        "01b51fcc-ed43-4cdb-ad1c-450f9986859b"
      ],
      "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
      "sent_date": "2018-02-22 15:02:07.190032",
      "subject": "Hello World",
      "survey": "33333333-22222-3333-4444-88dc018a1a4c",
      "thread_id": "78e3caa6-2e27-4ad3-bd38-168b2cc3ef5d"
    },
    {
      "@msg_from": {
        "emailAddress": "cblanc@hotmail.co.uk",
        "firstName": "Chandana",
        "id": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
        "lastName": "Blanchet",
        "sampleUnitType": "BI",
        "status": "ACTIVE",
        "telephone": "+443069990854"
      },
      "@msg_to": [
        {
          "emailAddress": "mock@email.com",
          "firstName": "BRES",
          "id": "BRES",
          "lastName": ""
        }
      ],
      "@business_details": {
        "id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
        "name": "Apple"
      },
      "_links": {
        "self": {
          "href": "http://localhost:5050/message/78e3caa6-2e27-4ad3-bd38-168b2cc3ef5d"
        }
      },
      "body": "Test",
      "collection_case": "collection case1",
      "collection_exercise": "collection exercise1",
      "from_internal": "False",
      "labels": [
        "SENT"
      ],
      "msg_from": "01b51fcc-ed43-4cdb-ad1c-450f9986859b",
      "msg_id": "78e3caa6-2e27-4ad3-bd38-168b2cc3ef5d",
      "msg_to": [
        "BRES"
      ],
      "business_id": "f1a5e99c-8edf-489a-9c72-6cabe6c387fc",
      "sent_date": "2018-02-22 15:02:07.133519",
      "subject": "Hello World",
      "survey": "33333333-22222-3333-4444-88dc018a1a4c",
      "thread_id": "78e3caa6-2e27-4ad3-bd38-168b2cc3ef5d"
    }
  ]
}
```

Note, See message get for descriptions of @msg_from, @msg_to and @business_details
[Get Message List](#get-message-list)

## Patch Conversation Metadata

`PATCH /threads/<thread_id>`

This is used to add/remove metadata to a conversation.  Below is a list of the parameters that can be
patched:

| Variable | Type| Notes |
| :---: | :---: | :--: |
| is_closed | `boolean` | Only internal users are allowed to close conversations.

Only the parameters you want to patch should be included in the call.

### Example JSON payload

```json
{
    "is_closed": true
}
```

There is no example response as a successful call will return a 204 with no extra content.
Below is a list of possible return values:

| Status | Notes |
| :---: | :---: |
| 204 | Successful call |
| 400 | Incorrect payload data supplied |
| 403 | Unauthorised.  |
| 404 | Thread id supplied not found in the database |
| 500 | Server-side error |

## Get Health

`GET /health`

Returns a simple indicator that the service is running. It is useful since it bypasses all aspects of the JWT.
So persistent 500s whilst health returns is often an indicator of incorrect JWT configuration.

### Example JSON Response

```json
{"status" : "healthy"}
```

## Get Health With Database Status

`GET /health/db`

Similar to health but validates that the current database connection is valid. Hence it is useful in various environments if database issues are suspected. Bypasses all aspects of the JWT.

### Example JSON Response

```json
{
  "errors" : "none",
  "status" : "healthy"
}
```

## Get Service Details

`GET /health/details`

Returns more detailed information about secure message including some of the environment variables. Bypasses all aspects of the JWT.

### Example JSON Response

```json
  {
  "API Functionality": {
    "/health": "Rest endpoint to provide application general health",
    "/health/db": "Rest endpoint to provide application database health",
    "/health/details": "Rest endpoint to provide application details",
    "/info": "Rest endpoint to provide application information",
    "/labels": "Get a count of unread messages",
    "/message/send": "Send message for a user",
    "/threads/<thread_id>": "Return list of messages for user",
    "/threads": "Return a list of threads for the user",
    "/messages/count": "Get count of unread messages",
    "/messages/modify/<message_id>": "Update message status by id"
  },
  "APP Log Level": "INFO",
  "NOTIFY VIA GOV NOTIFY": "0",
  "Name": "ras-secure-message",
  "RAS PARTY SERVICE HOST": "ras-party-service-sit.apps.devtest.onsclofo.uk",
  "RAS PARTY SERVICE PORT": "80",
  "RAS PARTY SERVICE PROTOCOL": "http",
  "Logging level": "DEBUG",
  "Using party service mock": false,
  "Version": "0.1.2"
}
```

## Get Service Version

`GET /info`

Similar to the health endpoints, it was added for consistency between services. Bypasses all aspects of JWT.

### Example JSON Response

```json
{
  "name": "ras-secure-message",
  "version": "0.1.2"
}
```
