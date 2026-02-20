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

CREATE OR REPLACE PROCEDURE securemessage.restore_deleted_conversations(p_backup_suffix TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Restore conversation
    EXECUTE format(
        'INSERT INTO securemessage.conversation SELECT * FROM securemessage._conversation_%s ON CONFLICT DO NOTHING',
        p_backup_suffix
    );
    -- Restore secure_message
    EXECUTE format(
        'INSERT INTO securemessage.secure_message SELECT * FROM securemessage._secure_message_%s ON CONFLICT DO NOTHING',
        p_backup_suffix
    );
    -- Restore status
    EXECUTE format(
        'INSERT INTO securemessage.status SELECT * FROM securemessage._status_%s ON CONFLICT DO NOTHING',
        p_backup_suffix
    );
    -- Drop backup tables
    EXECUTE format('DROP TABLE IF EXISTS securemessage._status_%s', p_backup_suffix);
    EXECUTE format('DROP TABLE IF EXISTS securemessage._secure_message_%s', p_backup_suffix);
    EXECUTE format('DROP TABLE IF EXISTS securemessage._conversation_%s', p_backup_suffix);
END;
$$;

