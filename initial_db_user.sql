
--
-- User: ras_secure_message, user for ras_secure_message microservice
--
-- Run with: psql -h localhost -p 5431 -U postgres -a -f initial_db_user.sql
--
DROP USER IF EXISTS ras_party;
CREATE USER ras_secure_message WITH PASSWORD 'password'
  SUPERUSER INHERIT CREATEDB CREATEROLE NOREPLICATION;
