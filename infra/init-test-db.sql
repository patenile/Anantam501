-- Create test user and database for backend tests
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'anantam') THEN
      CREATE USER anantam WITH PASSWORD 'supersecret';
   END IF;
END $$;

CREATE DATABASE anantam_test OWNER anantam;
