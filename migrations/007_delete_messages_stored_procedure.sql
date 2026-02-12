CREATE OR REPLACE PROCEDURE securemessage.delete_closed_conversations(p_close_at TIMESTAMP)
LANGUAGE plpgsql
AS $$
DECLARE
    backup_suffix TEXT := TO_CHAR(NOW(), 'YYYYMMDDHH24MISS');
BEGIN
    -- Backup and delete from status
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS securemessage._status_%s AS SELECT * FROM securemessage.status WHERE msg_id IN (SELECT msg_id FROM securemessage.secure_message WHERE thread_id IN (SELECT id FROM securemessage.conversation WHERE closed_at < $1 AND is_closed = true))',
        backup_suffix
    ) USING p_close_at;

    DELETE FROM securemessage.status
    WHERE msg_id IN (
        SELECT msg_id FROM securemessage.secure_message
        WHERE thread_id IN (
            SELECT id FROM securemessage.conversation
            WHERE closed_at < p_close_at AND is_closed = true
        )
    );

    -- Backup and delete from secure_message
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS securemessage._secure_message_%s AS SELECT * FROM securemessage.secure_message WHERE thread_id IN (SELECT id FROM securemessage.conversation WHERE closed_at < $1 AND is_closed = true)',
        backup_suffix
    ) USING p_close_at;

    DELETE FROM securemessage.secure_message
    WHERE thread_id IN (
        SELECT id FROM securemessage.conversation
        WHERE closed_at < p_close_at AND is_closed = true
    );

    -- Backup and delete from conversation
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS securemessage._conversation_%s AS SELECT * FROM securemessage.conversation WHERE closed_at < $1 AND is_closed = true',
        backup_suffix
    ) USING p_close_at;

    DELETE FROM securemessage.conversation
    WHERE closed_at < p_close_at AND is_closed = true;
END;
$$;