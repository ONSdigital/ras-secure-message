# Secure Message High Latency Request Investigation 

## Aim of document 

To identify and propose possible solutions, with effort, to reduce latency in ROPs  

## Scope 

The ROPs endpoint ```messages/<selected_survey>```, which includes code in ROPs, Secure Message and Party service
 
## Current situation 

Using Preprod and the BRES mailbox the approximate latency are follows 

#### Open messages  

UI load time: 7 seconds  

Query insight: 

 ![query insights open messages](/images/query-insights-open-messages.png)

#### Close messages:  

UI load time: 26 seconds 

Query insight: 

![query insights closed messages](/images/query-insights-closed-messages.png)

#### Ru_ref search:  

UI load time: 10 seconds 

Query insight: 

![query insights ru_ref messages](/images/query-insights-ru_ref-messages.png)
 

## Analyses 

All 3 suffer from the same 3 problems,  

- The party service is being called too many times and returning excess data (thousands of rows). The query in party isn’t particularly slow, but the multiple calls and processing is taking 3 to 4 seconds  

- The code in ROPs is causing multiple counts to be made unnecessarily 

- The query and model in SM are inefficient leading to excessive joins 


N.B Open message are considerably less affected by issues 2 and 3 due to the volume of data. open conversation in pre-prod: 9,577, closed 450k, with approximately 2.5 secure message per conversation 

 
### Party service 

After a pagination object has been created, SM calls to the party service to fill in the business details, it needs just the name and who it is from, but it gets back this 

```bash
[{'@business_details': {'associations': [{'businessRespondentStatus': 'ACTIVE', 'enrolments': [{'enrolmentStatus': 'ENABLED', 'surveyId': '02b9c366-7397-42f7-942a-76dc5876d86d'}], 'partyId': '5c185011-a174-41e1-81cc-eeb9a8db673f'}], 'id': '4be6b869-d8be-4299-8bd6-7cb4e1145401', 'name': 'RUNAME1_COMPANY1 RUNNAME2_COMPANY1', 'sampleSummaryId': '5b210fe8-9596-42dc-b4e3-bcac0161aaa2', 'sampleUnitRef': '49900000001', 'sampleUnitType': 'B', 'trading_as': 'TOTAL UK ACTIVITY'}, '@msg_from': {'emailAddress': 'uaa_user@ons.gov.uk', 'firstName': 'ONSname', 'id': '25a7f019-14c5-46d3-83bc-7e409752df58', 'lastName': 'User'}, '@msg_to': [{'associations': [{'businessRespondentStatus': 'ACTIVE', 'enrolments': [{'enrolmentStatus': 'ENABLED', 'surveyId': '02b9c366-7397-42f7-942a-76dc5876d86d'}], 'partyId': '4be6b869-d8be-4299-8bd6-7cb4e1145401', 'sampleUnitRef': '49900000001'}], 'emailAddress': 'example@example.com', 'firstName': 'john', 'id': '5c185011-a174-41e1-81cc-eeb9a8db673f', 'lastName': 'doe', 'sampleUnitType': 'BI', 'status': 'ACTIVE', 'telephone': '07772257772'}], '_links': {'self': {'href': 'http://localhost:5050/message/156fe6a1-3f84-490c-b325-009ed8e6ed07'}}, 'body': 'test body', 'business_id': '4be6b869-d8be-4299-8bd6-7cb4e1145401', 'case_id': '', 'exercise_id': '', 'from_internal': True, 'labels': ['SENT'], 'msg_from': '25a7f019-14c5-46d3-83bc-7e409752df58', 'msg_id': '156fe6a1-3f84-490c-b325-009ed8e6ed07', 'msg_to': ['5c185011-a174-41e1-81cc-eeb9a8db673f'], 'read_date': 'None', 'sent_date': '2025-10-07 08:32:41.694830', 'subject': 'test', 'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d', 'thread_id': '156fe6a1-3f84-490c-b325-009ed8e6ed07'}] 
```

The real issue is hidden in the above JSON and is down to how we store business attributes for every enrolment. This has a knock-on effect for both the query and the associations list which can be thousands in length, meaning slow processing time 

#### Possible Solution 

Call the party service once and return just the data needed, using the last enrolment attributes. This solution has been used in other places, most recently enrolments 

#### Effort / latency reduction 

Medium / Good 



### Record counts are duplicated 

Both the pagination object and the [tab count](https://github.com/ONSdigital/response-operations-ui/blob/main/response_operations_ui/views/messages.py#L497) are counting the records independently, adding to the latency. For open/closed messages it is unnecessary, for ru_ref searches the tab count is used but adds little value. 

![ru_ref tab counts](/images/ru_ref_tab_counts.png)

#### Possible Solution 

Use the pagination count attribute for open and closed messages and remove the other count. Check if the tab counts are still needed for ru_ref searches, if they still do, maintain functionality, but investigate a better solution (see below) 

#### Effort / latency reduction 

Low / Good 


### The query in Secure Message. 

There is a clear separation in each type 

#### Open 

Although it could be improved, I don’t believe the query for open messages is worth any immediate effort, unless it can be tied into improvements with closed/ru_ref searches, this is due to the volume of records not being significant. 

#### Possible Solution 

Improve the query and add indexes, but this would be by far the least in priority compared to the others on this document 

#### Effort / latency reduction 

Medium / very low 


#### Closed 

This is bordering on unusable due to the volume of data and the model. The model forces the conversation table and SM table to be joined, which leads to literally over a million records in preprod. This is painfully slow to process as seen by query analyzer 

#### Possible Solution 

This is purely down to the volume of data rather than the model. The query could be improved and indexes added to make things quicker, but the amount of conversations/message are to blame. If data can’t be deleted my suggestion would be to limit the amount the UI can view.  

Handily the conversation table has a closed_at time, which could be harnessed to show less, maybe 6 months (of even parametrize). I do think it’s important to understand how the business use closed messages, as I can see no logic in having a pagination object produce thousands of pages.  

The relationship of how ru_ref is being used is also important here as if that is their primary way of finding old messages, then we can allow that to query greater history, whilst limiting the amount for the closed tab 

#### Effort / latency reduction 

Low – high (depending on solution)/ very high 


#### Ru_ref search 

This suffers more from the tab counting [linearly calling](https://github.com/ONSdigital/ras-secure-message/blob/main/secure_message/repository/retriever.py#L94)  each category than the SM query itself 

#### Possible Solution 

The code needs a rewrite with regards to how they works, it should call once and more intelligently. I am however dubious there is much value in them at all for the cost and would explore removing them.  

#### Effort / latency reduction 

Low / high 


## Other observations 

### Pagination object count 

There is a clear warning in the docs that the [SqlAlchemy pagination count](https://flask-sqlalchemy.readthedocs.io/en/stable/api/#flask_sqlalchemy.SQLAlchemy.paginatemight could be slow or not appropriate for complicated or large queries, this might be worth looking into if latency is still an issue after implementing some of the above. We currently use it, but a more efficient solution might be possible 