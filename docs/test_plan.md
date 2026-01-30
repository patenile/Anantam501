# Test Documentation: Anantam Home Interior Design Collaboration App

## Overview
This document details the current and planned test coverage for the Anantam application, including the purpose and scope of each test type. It is intended to guide developers and reviewers in understanding the quality and reliability checks in place for both backend and frontend components.

---

## 1. Backend Tests
### 1.7. More Advanced PostgreSQL Scenarios (Implemented)
- **Location:** `backend/tests/test_postgres_more.py`
- **Framework:** pytest, psycopg2, SQLAlchemy
- **Purpose:** Test advanced PostgreSQL features: partitioned tables, triggers, views, materialized views, full-text search, time zones, large objects, and extension usage.
- **Tests Implemented:**
  - `test_partitioned_table_insert_and_select`: Validates partitioned table insert/select and partition routing.
  - `test_trigger_functionality`: Ensures triggers and trigger functions work (e.g., auto-updating timestamps).
  - `test_views_and_materialized_views`: Verifies creation and querying of views and materialized views.
  - `test_full_text_search`: Checks full-text search capabilities and correct results.
  - `test_time_zone_handling`: Ensures correct handling and storage of time zone-aware timestamps.
  - `test_large_object_usage`: Validates large object (LOB) storage and retrieval.
  - `test_extension_usage`: Ensures extensions (e.g., hstore) can be created, used, and dropped.
- **What They Test:**
  - The app’s ability to use and manage advanced PostgreSQL features in real-world scenarios.
  - That the DB layer is robust, flexible, and ready for complex production use cases.
- **Why These Tests Are Needed:**
  - To ensure the app can safely leverage the full power of PostgreSQL.
  - To catch subtle bugs and integration issues with advanced DB features before production.
  - To provide confidence for future DB design and feature expansion.
### 1.6. Advanced PostgreSQL Scenarios (Implemented)
- **Location:** `backend/tests/test_postgres_extra.py`
- **Framework:** pytest, psycopg2, SQLAlchemy
- **Purpose:** Test advanced and real-world PostgreSQL features: foreign keys, composite indexes, JSONB, array types, permissions, performance, and concurrent access.
- **Tests Implemented:**
  - `test_foreign_key_and_cascade`: Verifies foreign key constraints and cascading deletes.
  - `test_composite_index`: Checks composite index creation and existence.
  - `test_jsonb_and_array_types`: Validates correct storage and retrieval of JSONB and array columns.
  - `test_permissions_and_error`: Ensures permission errors are raised for invalid users.
  - `test_concurrent_access`: Simulates concurrent inserts to test thread safety and DB locking.
  - `test_performance_bulk_insert`: Measures and validates bulk insert performance and correctness.
- **What They Test:**
  - Advanced DB features and edge cases in a dedicated test schema/table.
  - That the app can safely use modern PostgreSQL features and handle concurrency.
  - Proper error handling and performance for production-like scenarios.
- **Why These Tests Are Needed:**
  - To ensure the app is robust for complex, high-load, and real-world DB usage.
  - To catch concurrency, permission, and advanced feature bugs before production.
  - To provide confidence in using PostgreSQL’s full feature set in your stack.
### 1.5. Advanced PostgreSQL Database Tests (Implemented)
- **Location:** `backend/tests/test_postgres_advanced.py`
- **Framework:** pytest, psycopg2, SQLAlchemy
- **Purpose:** Ensure robust, real-world DB coverage by testing CRUD, transactions, constraints, data types, and error handling using both raw SQL and SQLAlchemy.
- **Tests Implemented:**
  - `test_crud_raw_sql`: Full insert, select, update, delete cycle using raw SQL.
  - `test_crud_sqlalchemy`: Full CRUD cycle using SQLAlchemy ORM.
  - `test_transaction_rollback`: Verifies rollback undoes changes as expected.
  - `test_unique_constraint`: Checks unique constraint enforcement and error on duplicate insert.
  - `test_data_types_and_casting`: Validates type casting and correct storage of values.
  - `test_error_handling`: Ensures errors are raised for invalid operations (e.g., NOT NULL violation).
- **What They Test:**
  - All major DB operations and edge cases in a dedicated test schema/table.
  - That both direct SQL and ORM-based approaches are reliable and consistent.
  - Proper transaction and constraint handling, and robust error reporting.
- **Why These Tests Are Needed:**
  - To catch subtle DB bugs/regressions before they reach production.
  - To ensure the app’s DB layer is safe, flexible, and standards-compliant.
  - To provide confidence in migrations, schema changes, and advanced DB usage.
### 1.4. PostgreSQL Schema and Table Creation Tests (Implemented)
- **Location:** `backend/tests/test_postgres_schema.py`
- **Framework:** pytest, psycopg2, SQLAlchemy
- **Purpose:** Ensure the application can create and clean up schemas and tables in PostgreSQL, using both raw SQL and SQLAlchemy, to verify DB flexibility and correctness.
- **Tests Implemented:**
  - `test_create_table_raw_sql`: Creates a schema and table using raw SQL (psycopg2), verifies existence, and cleans up.
  - `test_create_table_sqlalchemy`: Creates a schema and table using SQLAlchemy ORM, verifies existence, and cleans up.
- **What They Test:**
  - Schema and table creation in a dedicated test schema (test_schema) and table (test_table).
  - That both direct SQL and ORM-based approaches work as expected in the test DB.
  - Proper cleanup of test artifacts to keep the DB clean for future tests.
- **Why These Tests Are Needed:**
  - To ensure the app can manage DB schemas/tables programmatically and flexibly.
  - To catch migration, permission, or DB config issues early in CI/CD.
  - To provide a foundation for CRUD, transaction, and advanced DB tests.
### 1.2. PostgreSQL Database Tests (Implemented)
- **Location:** `backend/tests/test_postgres_connection.py`
- **Framework:** pytest, psycopg2, SQLAlchemy
- **Purpose:** Ensure the application can connect to PostgreSQL, authenticate, and handle connection errors robustly, using both raw SQL and SQLAlchemy.
- **Tests Implemented:**
  - `test_psycopg2_connection`: Verifies direct connection to PostgreSQL using psycopg2 and basic query execution.
  - `test_sqlalchemy_connection`: Verifies connection to PostgreSQL using SQLAlchemy engine and query execution.
  - `test_authentication_failure`: Ensures authentication fails with incorrect credentials, confirming security and error handling.
- **What They Test:**
  - Database connectivity, authentication, and error handling at the driver and ORM level.
  - That the test environment is correctly configured and isolated (using test DB only).
- **Why These Tests Are Needed:**
  - To catch DB connection/configuration issues early in CI/CD.
  - To ensure the app fails securely and predictably on DB auth errors.
  - To provide a foundation for more advanced DB tests (schema, CRUD, transactions, etc.).
### 1.1. Integration/API Tests (Implemented)
- **Location:** `backend/tests/test_auth.py`
- **Framework:** pytest
- **Purpose:** Test backend authentication endpoints as a whole, including DB, auth, and business logic, with a focus on real-world edge cases and security.
- **Tests Implemented:**
  - `test_register`: Ensures user registration endpoint works, including password truncation and hashing.
  - `test_login`: Validates login endpoint, correct credential handling, and token issuance.
  - `test_me`: Checks authenticated user info retrieval for logged-in users.
  - `test_register_invalid_email`: Verifies registration fails with an invalid email (ensures email format validation is enforced).
  - `test_register_short_password`: Verifies registration fails with a too-short password (enforces password policy for security).
  - `test_register_duplicate_user`: Ensures duplicate registration attempts are rejected (prevents account takeover and DB errors).
  - `test_login_wrong_password`: Ensures login fails with an incorrect password (prevents unauthorized access).
  - `test_login_nonexistent_user`: Ensures login fails for non-existent users (prevents information leakage and brute force).
- **What They Test:**
  - Input validation, error handling, and correct DB writes/reads for authentication flows.
  - Password security logic (truncation, hashing, bcrypt integration, minimum length enforcement).
  - Proper error codes and messages for all edge cases, ensuring robust and predictable API behavior.
- **Why These Tests Are Needed:**
  - To prevent common security vulnerabilities (weak passwords, duplicate accounts, invalid input).
  - To ensure the backend enforces business rules and security policies as intended.
  - To catch regressions and integration issues early in CI/CD pipelines.
  - To provide confidence that the authentication system is robust against real-world attack scenarios.


### 1.3. Migration/Data Integrity Tests (Implemented)
- **Location:** `backend/tests/test_migrations.py`
- **Framework:** pytest, Alembic, SQLAlchemy
- **Purpose:** Ensure Alembic migrations apply cleanly, are idempotent, and data/schema remain consistent through upgrade/downgrade cycles.
- **Tests Implemented:**
  - `test_migration_upgrade`: Applies all migrations to a fresh test DB and verifies tables are created.
  - `test_migration_downgrade`: Upgrades then downgrades the DB, ensuring all tables except Alembic's version table are dropped (xfail if not possible due to known Postgres/SQLAlchemy teardown limitations).
  - `test_migration_idempotence`: Runs upgrade/downgrade multiple times to ensure migrations are idempotent and do not fail on repeated application.
- **What They Test:**
  - Alembic migration scripts, schema creation, and rollback.
  - DB state after upgrade/downgrade, including edge cases and teardown.
  - That destructive operations only affect the test DB, never the main DB.
- **Why These Tests Are Needed:**
  - To prevent migration errors from reaching production.
  - To ensure DB schema changes are safe, reversible, and repeatable.
  - To catch destructive migration bugs and DB config issues early in CI/CD.
  - To document and track known limitations (e.g., teardown xfail) for future improvement.

### 1.3. Migration/Data Integrity Tests (Planned)
- **Purpose:** Ensure Alembic migrations apply cleanly and data remains consistent.
- **Planned Tests:**
  - Migration on fresh DB, upgrade/downgrade cycles.
  - Data preservation and schema validation after migrations.

---

## 2. Frontend Tests

### 2.1. Unit Tests (Implemented)
- **Location:** `frontend/src/App.test.jsx`
- **Framework:** Vitest, Testing Library
- **Purpose:** Verify React components render and behave as expected in isolation.
- **Tests Written:**
  - `App` renders the main heading.
- **What They Test:**
  - Component rendering, presence of key UI elements.

### 2.2. Integration/UI Tests (Planned)
- **Purpose:** Test component interactions, state changes, and API integration.
- **Planned Tests:**
  - Simulate user actions (form fill, button click) and check UI updates.
  - Mock API calls and verify data flow from backend to UI.
- **What They Will Test:**
  - User experience, error messages, and correct API integration.

### 2.3. End-to-End (E2E) Tests (Planned)
- **Purpose:** Automate real user flows across the stack (frontend + backend + DB).
- **Planned Tools:** Cypress or Playwright
- **Planned Tests:**
  - User registration, login, and dashboard navigation.
  - Full CRUD flows for design collaboration features.
- **What They Will Test:**
  - Complete system reliability, cross-service integration, and regression prevention.

---

## 3. CI/CD Pipeline Tests (Planned)
- **Purpose:** Ensure all tests run automatically on every push/PR.
- **Planned Steps:**
  - Install dependencies, run backend and frontend tests, build images, and (optionally) run E2E tests in CI.
- **What They Will Test:**
  - Prevent broken code from merging, enforce code quality and reliability.

---

## Summary Table
| Test Type         | Status      | Purpose/Scope                                      |
|-------------------|------------|----------------------------------------------------|
| Backend Unit      | Implemented| Auth endpoints, password logic, DB ops              |
| Backend API       | Planned    | End-to-end API, error handling, DB state            |
| Migration         | Planned    | Alembic migrations, schema/data integrity           |
| Frontend Unit     | Implemented| Component rendering, UI presence                    |
| Frontend UI       | Planned    | User actions, state, API integration                |
| E2E               | Planned    | Full user flows, cross-service integration          |
| CI/CD             | Planned    | Automated test runs, build checks                   |

---

## Next Steps
- Implement backend API and migration tests.
- Expand frontend tests to cover user interactions and API integration.
- Set up E2E automation and CI/CD pipeline for full-stack reliability.

---

For any new feature, add or update tests in the relevant section and update this document to reflect coverage.

Integration/API tests:

Test backend endpoints from the frontend or with tools like Postman, pytest, or supertest.
Ensure authentication, registration, and data flows work end-to-end.
Frontend integration/UI tests:

Use Testing Library or Cypress/Playwright to simulate user interactions and verify UI updates and API integration.
Database migrations and data integrity:

Test Alembic migrations on a fresh database and with real upgrade/downgrade scenarios.
End-to-end (E2E) tests:

Automate browser-based flows (login, registration, CRUD) using Cypress or Playwright.
CI/CD pipeline:

Set up GitHub Actions or similar to run all tests automatically on push/PR.


Integration/API tests:

Test backend endpoints from the frontend or with tools like Postman, pytest, or supertest.
Ensure authentication, registration, and data flows work end-to-end.
Frontend integration/UI tests:

Use Testing Library or Cypress/Playwright to simulate user interactions and verify UI updates and API integration.
Database migrations and data integrity:

Test Alembic migrations on a fresh database and with real upgrade/downgrade scenarios.
End-to-end (E2E) tests: Below are the command to run E2E tests manually
cd e2e
npm install
npx playwright test
npx playwright test --ui

Automate browser-based flows (login, registration, CRUD) using Cypress or Playwright.
CI/CD pipeline:

Set up GitHub Actions or similar to run all tests automatically on push/PR.
Would you like to start with A