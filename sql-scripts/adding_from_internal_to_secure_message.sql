-- Script to add a from_internal column to secure_message
-- and populate from_internal to true
-- for messages that were sent from internal user
-- Also drops the internal_sent_audit table and actors tables if present


Alter table securemessage.secure_message ADD from_internal Bool Default False;

update securemessage.secure_message m
set from_internal = true
where m.msg_id in (select s.msg_id from securemessage.status s where s.label='SENT');


DROP TABLE IF EXISTS securemessage.internal_sent_audit;
DROP TABLE IF EXISTS securemessage.actors;