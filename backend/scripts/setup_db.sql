-- Campus Chommie: create the database role and databases (PostgreSQL 16+).
--
-- Run ONCE per laptop, as the postgres admin user, from the repo root:
--
--   psql -U postgres -h localhost -v app_password="YOUR-DB-PASSWORD" -f backend/scripts/setup_db.sql
--
-- Safe to run again: it only creates what is missing, never drops or
-- changes anything. Use the same password in backend/.env
-- (POSTGRES_PASSWORD). Schemas and tables are NOT created here: run
-- `flask db upgrade` afterwards, which builds them from the migrations.

\set ON_ERROR_STOP on

SELECT format('CREATE ROLE campus_chommie LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'campus_chommie')
\gexec

SELECT 'CREATE DATABASE campus_chommie_dev OWNER campus_chommie'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'campus_chommie_dev')
\gexec

SELECT 'CREATE DATABASE campus_chommie_test OWNER campus_chommie'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'campus_chommie_test')
\gexec

\echo 'Done: role campus_chommie, databases campus_chommie_dev and campus_chommie_test are ready. Next: flask db upgrade'
