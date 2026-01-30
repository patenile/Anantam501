# TODO


## Disabled Tests and Services (Temporary)

- Backend, migration, and all PostgreSQL-related tests (test_postgres*, test_postgres_schema.py) are currently disabled from pre-commit. These should be re-enabled once the database and backend are ready for integration testing.
- The PostgreSQL (db) service is commented out in infra/docker-compose.yml. Re-enable it when you want to run full backend and migration tests.

**Reminder:**
- Update backend/package.json and the root package.json to re-enable backend/e2e and PostgreSQL-related pre-commit scripts.
- Uncomment the db service in infra/docker-compose.yml to restore PostgreSQL.
- Remove the test exclusion for test_postgres* and test_postgres_schema.py in backend/package.json when ready to re-enable these tests.
