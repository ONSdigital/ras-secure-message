ALTER TABLE securemessage.secure_message
ADD COLUMN IF NOT EXISTS sent_at timestamp,
ADD COLUMN IF NOT EXISTS read_at timestamp
