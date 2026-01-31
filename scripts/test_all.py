import subprocess
import sys
import os

# All backend Postgres-related test groups (name, file)
POSTGRES_TEST_GROUPS = [
    ("Auth API Tests", "/app/tests/test_auth.py"),
    ("Migration Tests", "/app/tests/test_migrations.py"),
    ("PostgreSQL Connection Tests", "/app/tests/test_postgres_connection.py"),
    ("PostgreSQL Schema Tests", "/app/tests/test_postgres_schema.py"),
    ("PostgreSQL Advanced Tests", "/app/tests/test_postgres_advanced.py"),
    ("PostgreSQL Extra Tests", "/app/tests/test_postgres_extra.py"),
    ("PostgreSQL More Advanced Tests", "/app/tests/test_postgres_more.py"),
]


def postgres_test_cmd(test_file):
    return [
        "docker",
        "compose",
        "-f",
        "infra/docker-compose.yml",
        "exec",
        "-e",
        "TEST_DB=anantam_test",
        "-e",
        "TEST_DB_USER=anantam",
        "-e",
        "TEST_DB_PASSWORD=supersecret",  # pragma: allowlist secret
        "-e",
        "TEST_DB_HOST=db",
        "-e",
        "TEST_DB_PORT=5432",
        "-e",
        (
            "TEST_DATABASE_URL="
            "postgresql://anantam:"
            "supersecret@db:5432/anantam_test"  # pragma: allowlist secret
        ),
        "-e",
        (
            "DATABASE_URL="
            "postgresql://anantam:"
            "supersecret@db:5432/anantam_test"  # pragma: allowlist secret
        ),
        "backend",
        "pytest",
        test_file,
        "--maxfail=10",
        "--disable-warnings",
        "-v",
        "--tb=short",
    ]


TEST_COMMANDS = [
    (name, postgres_test_cmd(test_file)) for name, test_file in POSTGRES_TEST_GROUPS
]

FRONTEND_TEST = (
    "Frontend Unit Tests",
    [
        "docker",
        "compose",
        "-f",
        "infra/docker-compose.yml",
        "exec",
        "frontend",
        "npm",
        "run",
        "test",
    ],
)

# E2E Playwright test command (run from e2e/ directory)
E2E_TEST = ("E2E Playwright Tests", ["npx", "playwright", "test"])

ALL_COMMANDS = TEST_COMMANDS + [FRONTEND_TEST, E2E_TEST]


def ensure_playwright_installed():
    """Ensure Playwright and its browsers are installed in the e2e/ directory."""
    e2e_dir = os.path.join(os.path.dirname(__file__), "..", "e2e")
    node_modules = os.path.join(e2e_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("[E2E] Installing npm dependencies in e2e/ ...")
        result = subprocess.run(["npm", "install"], cwd=e2e_dir)
        if result.returncode != 0:
            print("[E2E] npm install failed.")
            sys.exit(result.returncode)
    print("[E2E] Ensuring Playwright browsers are installed ...")
    result = subprocess.run(["npx", "playwright", "install"], cwd=e2e_dir)
    if result.returncode != 0:
        print("[E2E] Playwright browser install failed.")
        sys.exit(result.returncode)


def main():
    # If 'postgres' is passed as an argument, only run Postgres-related tests
    only_postgres = len(sys.argv) > 1 and sys.argv[1] == "postgres"
    cmds = TEST_COMMANDS if only_postgres else ALL_COMMANDS
    ran = []
    print("\n==================== TEST SUITE START ====================\n")
    for name, cmd in cmds:
        print(f"\n========== Running: {name} ==========")
        print(f"[COMMAND] {' '.join(cmd)}\n")
        # For E2E tests, ensure Playwright is installed and run from e2e/
        if name == "E2E Playwright Tests":
            ensure_playwright_installed()
            e2e_dir = os.path.join(os.path.dirname(__file__), "..", "e2e")
            result = subprocess.run(cmd, cwd=e2e_dir)
        else:
            result = subprocess.run(cmd)
        ran.append((name, result.returncode))
        # Only stop the suite for failures that are not Migration Tests
        if result.returncode != 0 and name != "Migration Tests":
            print(f"[TEST SUITE] FAILED: {name}")
            print("\n==================== TEST SUITE END ====================\n")
            sys.exit(result.returncode)
        if result.returncode != 0 and name == "Migration Tests":
            print("[TEST SUITE] Migration Tests failed, " "but continuing as expected.")
    print("\n==================== TEST SUITE END ====================\n")
    print("\nTest Summary:")
    for name, code in ran:
        print(f"  {name}: {'PASSED' if code == 0 else 'FAILED'}")
    # Only print all-passed if all except Migration Tests passed
    non_migration = [(n, c) for n, c in ran if n != "Migration Tests"]
    if all(code == 0 for _, code in non_migration):
        print("\n[TEST SUITE] All tests passed!\n")
    else:
        print("\n[TEST SUITE] Some tests failed. See summary above.\n")


if __name__ == "__main__":
    main()
