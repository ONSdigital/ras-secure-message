-- NOTE: these are not particularly fast queries because of the weird table structure
-- BIG NOTE: Please do not run any of the update/delete queries without being absolutely sure you want to. Do not even copy them into a live SQL window!

-- This statement will return all thread IDs that have had no activity in over 1 year
select c.id from conversation c join secure_message sm on c.id = sm.thread_id group by c.id having MAX(sm.sent_at) < (NOW() - interval '1 year');

-- In order to delete these messages, you would either hard delete using:
delete from conversation c where c.id in (select c.id from conversation c join secure_message sm on c.id = sm.thread_id group by c.id  
having MAX(sm.sent_at) < (NOW() - interval '1 year'));

-- or soft delete using:
update conversation c where c.id in (select c.id from conversation c join secure_message sm on c.id = sm.thread_id group by c.id  
having MAX(sm.sent_at) < (NOW() - interval '1 year')) set c.deleted = TRUE;
-- This would require a new column (conversation.deleted) as well as front-end changes to not show deleted threads. 
-- This is preferable, as it gives us time to undelete anything the business ended up regretting losing without having to restore a whole backup.
-- NOTE: The threads should be deleted *AFTER* the messages inside the threads have been.

-- This statement will return all messages in threads that have had no activity in over 1 year
select * from secure_message sm where sm.thread_id in (select c.id from conversation c join secure_message sm on c.id = sm.thread_id group by c.id  
having MAX(sm.sent_at) < (NOW() - interval '1 year'));

-- In order to delete these messages, you would either hard delete:
delete from secure_message sm where sm.thread_id in (select c.id from conversation c join secure_message sm on c.id = sm.thread_id group by c.id  
having MAX(sm.sent_at) < (NOW() - interval '1 year'));

-- or add the new column/front-end changes and soft delete:
update secure_message sm where sm.thread_id in (select c.id from conversation c join secure_message sm on c.id = sm.thread_id group by c.id  
having MAX(sm.sent_at) < (NOW() - interval '1 year')) set sm.deleted = TRUE;
-- Like with threads, this should ideally be done with the soft delete