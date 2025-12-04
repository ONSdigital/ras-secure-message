# Deleting closed message threads after 12 months


## Scope
I want to know if it is possible to identify closed message threads that haven’t been opened by external and internal users in the last 12 months.

So that we can explore what is feasible for an automated message deletion job in the backend whilst mitigating impact on the end user


## Current situation
On deploying the secure message application 3 tables are created, secure message, conversation and status


###  Secure message 
The individual message, it includes details relating to the message, as well as events, which is limited to when it was sent and read. When a message is created the read_at is left blank, it gets populated on the first read, it is not updated after that 


### Conversation 
The general container for all related secure messages, i.e the initial message and any replies, if internal or external. It keeps record of whether the conversation is closed and if it is when and by whom


### Status 
Message dependent, it records basic information regarding whos inbox it is in and the state of the message (read, sent etc). Similar to secure message a record is kept if it has not been read, but it gets deleted once it has


## Summary
We can only tell when a message has been sent, read initially or closed. We can use the closed date to delete conversations after 12 months, but not the read_at date/time


## What we could do

1. Write a cron job to delete messages related to the closed date (5 SP*)

2. We could write code to update the read_at every time a message is viewed, then use that to delete, however I don’t recommend that due to the
   - The additional traffic to the database
   - read_at feels like it might have been implemented for enforcement, this could confuse the initial reason for its inclusion
   - Updating what is a hidden field to a user/respondent to control deletion of a conversation feels inappropriate.  Knowing when a conversation is going to be deleted seems important at least internally, having ambiguity on when it might happen should be avoided


3. Use the closed_date to delete after 12 months, but add an extra field to the database to override deletion and then give that control on the UI for closed messages, with guidance when it would be deleted. This needs a deeper dive and researching properly, but seems feasible at reasonable development cost. 
Adding an extra field on the UI (just ROPS), linked to a field in the db - 8SP* (you would still need the cron job as well)


*I’ve included estimates as they are a good way of assessing effort and complexity, however without detail of requirements and no input from other developers they are a rough guide.
