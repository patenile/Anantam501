# Debugging PostgreSQL Database Issues in Dockerized Test Environments

This document outlines step-by-step procedures for debugging persistent schema or table issues in a PostgreSQL database managed by Docker Compose, especially when tables appear unexpectedly before migrations.

## 1. Remove Docker Volumes to Guarantee a Fresh Database

To ensure no persistent data remains, stop all services and remove all associated Docker volumes:

```
docker compose -f infra/docker-compose.test.yml down -v
```

## 2. Manually Inspect the Database State Before Migrations

Start only the database service and connect to the test database to list all tables:

```
docker compose -f infra/docker-compose.test.yml up -d db

docker compose -f infra/docker-compose.test.yml exec -T db psql -U anantam -d anantam_test -c "\dt"
```

If you see tables (e.g., "users") before running migrations, something outside your migration scripts is creating them.

## 3. Manually Remove Problem Tables

To drop a problematic table (e.g., "users") and verify removal:

```
docker compose -f infra/docker-compose.test.yml exec -T db psql -U anantam -d anantam_test -c "DROP TABLE IF EXISTS users CASCADE;"
docker compose -f infra/docker-compose.test.yml exec -T db psql -U anantam -d anantam_test -c "\dt"
```

## 4. Rerun Test Orchestration

After confirming the database is clean, rerun your test orchestration to ensure migrations and tests are fully under your control:

```
python scripts/test_with_services.py
```

## 5. Investigate Hidden or System-Level SQL Scripts

If tables still appear unexpectedly:
- Check for any `.sql` files in your project, especially in `infra/` or `backend/`.
- Check for hidden directories like `docker-entrypoint-initdb.d/`.
- Review your Docker Compose volume mounts for any unexpected SQL scripts.

## 6. Change the Test Database Name (Advanced)

If the issue persists, try changing the test database name in your Compose and scripts to fully isolate the cause.

---

**Use this checklist whenever you encounter persistent or unexplained schema issues in your Dockerized PostgreSQL test environment.**
