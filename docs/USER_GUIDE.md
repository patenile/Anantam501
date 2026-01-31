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

## 9. Running All Backend, Frontend, and E2E Tests Together

To run all backend, frontend, and end-to-end (E2E) tests in a single command, use the following Python script:

```sh
python scripts/test_with_services.py
```

### What this command does:
- Spins up all required services (database, backend, frontend, etc.) using Docker Compose.
- Runs all backend tests (pytest), all frontend tests (npm/vitest), and all E2E tests (Playwright) in sequence.
- Cleans up and tears down all services after tests complete.
- Prints a summary of test results for each layer (backend, frontend, e2e).

#### Optional flags:
- `--no-frontend` — Skip frontend tests.
- `--no-e2e` — Skip E2E tests.
- `--no-teardown` — Keep services running after tests (for debugging).
- `--ci` — Print CI-friendly output.

### When to use this script:
- For full-stack validation before a release or major merge.
- In CI/CD pipelines to ensure all layers pass together.
- When you want to test the integration of backend, frontend, and E2E flows in one go.

### When to use `npm run pre-commit` instead:
- For fast local checks of code style, linting, and frontend unit tests before committing code.
- When backend or database services are not available or you want to skip integration tests.

**Best Practice:**
- Use `python scripts/test_with_services.py` for full-stack or CI validation.
- Use `npm run pre-commit` for quick local checks and code quality enforcement.

See the script's help for more options:
```sh
python scripts/test_with_services.py --help
```
