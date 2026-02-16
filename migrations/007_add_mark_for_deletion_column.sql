-- Migration to add mark_for_deletion as a nullable boolean column to conversation table
ALTER TABLE securemessage.secure_message ADD COLUMN mark_for_deletion BOOLEAN;

