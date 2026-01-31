## 8. Test Environment Variables: .env.test

For all automated tests and CI runs, test-specific secrets and variables are stored in backend/.env.test. This file is used to configure the test database and any other secrets needed for safe, isolated test execution.

- **Location:** backend/.env.test
- **Typical contents:**
  ```env
  TEST_DB=anantam_test
  TEST_DB_USER=anantam
  TEST_DB_PASSWORD=supersecret  # pragma: allowlist secret
  TEST_DB_HOST=localhost
  TEST_DB_PORT=5432
  TEST_DATABASE_URL=postgresql://anantam:supersecret@localhost:5432/anantam_test  # pragma: allowlist secret
  # Add any other test-only secrets here
  ```
- **Usage:**
  - Loaded automatically by scripts/test_with_services.py and the backend test setup.
  - Never commit real secrets or production credentials to this file.
  - You can safely change these values for local test runs as needed.

**Best Practice:**
Keep .env.test for test-only secrets and .env for your main app/dev environment. This ensures test runs are always isolated and reproducible.

## 7. Docker Compose Usage: Design/Dev vs. Test

The project uses two separate Docker Compose files to keep development and test environments isolated:

- **docker-compose.yml** (in infra/):

  - Use this for normal development, design, and running the main application stack.
  - Reads environment variables from your .env file (not committed to version control).
  - Safe for local development and design work.
  - Example:
    ```sh
    cd infra
    docker compose up -d
    # ...work on your app, then:
    docker compose down -v
    ```

- **docker-compose.test.yml** (in infra/):
  - Use this for running automated tests (backend, frontend, E2E) and CI/CD.
  - Hardcodes test database user, password, and DB name for safety and reproducibility.
  - Mounts a test DB initialization script to ensure the test DB is always ready.
  - Used by scripts/test_with_services.py and in CI pipelines.
  - Example:
    ```sh
    cd infra
    docker compose -f docker-compose.test.yml up -d
    # ...run tests, then:
    docker compose -f docker-compose.test.yml down -v
    ```

**Best Practice:**
Always use docker-compose.test.yml for test automation and CI, and docker-compose.yml for your main app/dev work. This keeps your real data and test data completely separate and safe.

# Anantam App: Quick Start & User Guide

## 1. Activating the Python Virtual Environment

To use the correct Python and pip for backend development:

```sh
source backend/.venv/bin/activate
```

## 2. Running the Master Control Script

- To validate your environment and test the stack:

```sh
python scripts/run_app.py
```

- To start the full application stack and keep it running:

```sh
python scripts/run_app.py --live
```

## 3. Stopping the Application Stack

- To stop all running containers (from another terminal):

```sh
cd infra
# Stop and remove containers, networks, and volumes
docker compose down -v
```

## 4. Additional Tips

- Always activate the virtual environment before installing new Python packages:
  ```sh
  source backend/.venv/bin/activate
  pip install <package>
  ```
- To rebuild the stack from scratch:
  ```sh
  python scripts/run_app.py --cleanup
  python scripts/run_app.py --build
  python scripts/run_app.py --live
  ```
- You can also use Docker Compose directly for advanced control:
  ```sh
  cd infra
  docker compose up -d
  docker compose logs -f
  docker compose down -v
  ```

## 5. Troubleshooting

- If you see errors about missing Python packages, re-run the setup:
  ```sh
  python scripts/run_app.py
  ```
- If you change .env or requirements.txt, re-run the setup to apply changes.

---

This guide ensures a smooth developer experience for starting, stopping, and managing the Anantam app. For more details, see the README.md or docs/ folder.

---

## 6. Code Quality Automation: npm run pre-commit

To run all code quality checks and tests before committing code, use:

```sh
npm run pre-commit
```

### What this command does:

- Runs linting (flake8 for backend, Prettier for frontend) to check code style.
- Runs code formatting checks (black for backend, Prettier for frontend).
- Runs automated tests for the frontend.
- Shows color-coded output: yellow for warnings, red for failures, green for passing tests.
- Warns you if backend, migration, or PostgreSQL-related tests are currently disabled.

### What is currently disabled (for future re-enabling):

- All backend, migration, and PostgreSQL-related tests (test_auth, test_migrations, test_postgres\*, test_postgres_schema.py) are excluded from pre-commit and will not run.
- This is to allow development and commits even if the database or backend is not available.
- The PostgreSQL (db) service is present in docker-compose.yml, but tests that require it are skipped in pre-commit.

### Future enhancements:

- Re-enable backend, migration, and PostgreSQL-related tests in pre-commit when integration testing is needed.
- Optionally add coverage reporting and upload to CI/CD.
- Add more granular linting or formatting rules as the project grows.
- Integrate additional security or dependency checks.

See todo.md for a checklist of what is currently disabled and how to re-enable.

Your setup is now robust and follows best practices for environment isolation, automation, and CI/CD integration. Here are a few optional but valuable adjustments you could consider for even greater reliability and developer experience:

Good to Have:

Add a README section or quickstart in USER_GUIDE.md explaining the difference between docker-compose.yml and docker-compose.test.yml, and how/when to use each.
Add a pre-test check in test_with_services.py to ensure Docker is running and the compose file exists.
Automatically clean up old test artifacts and reports to save disk space.
Add a test summary output at the end of test_with_services.py for local runs (not just CI).
Use .env.test for all test-specific secrets and variables, and document this in your guides.
Add a GitHub Actions status badge to your README for instant CI visibility.
Periodically review and prune unused Docker volumes/networks with a maintenance script.
Missing (if not already present):

Database migration step before running backend tests (e.g., alembic upgrade head).
Test data seeding for integration/E2E tests.
More granular test selection (by tag, file, or changed code).
Notification for test flakiness or repeated failures.
Let me know if you want to implement any of these now, or if you’re ready to focus on validating your new workflow!
