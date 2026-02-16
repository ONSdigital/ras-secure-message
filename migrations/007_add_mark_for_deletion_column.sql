-- Migration to add mark_for_deletion as a nullable boolean column to secure_message table
ALTER TABLE securemessage.secure_message ADD COLUMN mark_for_deletion BOOLEAN;

