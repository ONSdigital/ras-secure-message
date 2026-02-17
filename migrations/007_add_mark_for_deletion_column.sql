-- Migration to add mark_for_deletion as a nullable boolean column to conversation table
ALTER TABLE securemessage.conversation ADD COLUMN IF NOT EXISTS mark_for_deletion BOOLEAN DEFAULT false;

