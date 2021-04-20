ALTER TABLE securemessage.conversation
ADD COLUMN IF NOT EXISTS category varchar default "SURVEY";