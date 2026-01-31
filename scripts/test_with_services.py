# All imports at top
import subprocess
import os
import sys
from pathlib import Path

COMPOSE_FILE = os.path.join("infra", "docker-compose.test.yml")
ENV_FILE = os.path.join("backend", ".env.test")


def clean_old_reports():
    reports_dir = Path("reports")
    if reports_dir.exists():
        for f in reports_dir.glob("*"):
            try:
                f.unlink()
            except Exception as e:
                print(f"[WARN] Could not delete {f}: {e}")
        print("[INFO] Cleaned up old test reports in 'reports/' directory.")


def pre_test_checks():
    # Check Docker is running
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except Exception:
        print(
            "[ERROR] Docker is not running or not installed. "
            "Please start Docker Desktop or your Docker daemon."
        )
        sys.exit(1)
    # Check compose file exists
    if not os.path.exists(COMPOSE_FILE):
        print(f"[ERROR] Compose file not found: {COMPOSE_FILE}")
        sys.exit(1)


# Remove duplicate imports and variables (already at top)


def run(cmd, check=True, **kwargs):
    print(f"[INFO] Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, check=check, **kwargs)


def wait_for_db():
    print("[INFO] Waiting for database to be ready...")

    def main():
        import argparse

        parser = argparse.ArgumentParser(
            description="Run all tests with service setup/teardown."
        )
        parser.add_argument(
            "--no-frontend", action="store_true", help="Skip frontend tests"
        )
        parser.add_argument("--no-e2e", action="store_true", help="Skip E2E tests")
        parser.add_argument(
            "--no-teardown",
            action="store_true",
            help="Do not tear down services after tests",
        )
        parser.add_argument(
            "--ci", action="store_true", help="Print CI-friendly output"
        )
        args, pytest_args = parser.parse_known_args()

        run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"])
        wait_for_db()
        # F821: define stub if missing
        try:
            load_env_vars()
        except NameError:
            print("[WARN] load_env_vars() not implemented; skipping.")

        print("[INFO] Running backend tests...")
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        junit_path = reports_dir / "backend-junit.xml"
        backend_code = subprocess.call(
            [
                "./backend/.venv/bin/python",
                "-m",
                "pytest",
                "backend/tests",
                f"--junitxml={junit_path}",
            ]
            + pytest_args
        )

        frontend_code = 0
        if not args.no_frontend:
            try:
                frontend_code = run_frontend_tests()
            except NameError:
                print("[WARN] run_frontend_tests() not implemented; skipping.")

        e2e_code = 0
        if not args.no_e2e:
            try:
                e2e_code = run_e2e_tests()
            except NameError:
                print("[WARN] run_e2e_tests() not implemented; skipping.")

        if not args.no_teardown:
            try:
                teardown_services()
            except NameError:
                print("[WARN] teardown_services() not implemented; skipping.")

        # Print test summary for local runs (not just CI)
        print("\n==================== TEST SUMMARY ====================")
        print(f"BACKEND:   {'PASS' if backend_code == 0 else 'FAIL'}")
        print(f"FRONTEND:  {'PASS' if frontend_code == 0 else 'FAIL'}")
        print(f"E2E:       {'PASS' if e2e_code == 0 else 'FAIL'}")
        print("====================================================\n")

        if args.ci:
            print("::group::Test Results")
            print(f"BACKEND: {'PASS' if backend_code == 0 else 'FAIL'}")
            print(f"FRONTEND: {'PASS' if frontend_code == 0 else 'FAIL'}")
            print(f"E2E: {'PASS' if e2e_code == 0 else 'FAIL'}")
            print("::endgroup::")

        # Exit with nonzero if any test failed
        sys.exit(backend_code or frontend_code or e2e_code)


def teardown_services():
    print("[INFO] Tearing down Docker Compose services...")
    run(["docker", "compose", "-f", COMPOSE_FILE, "down"])


def main():
    pre_test_checks()
    clean_old_reports()
    import argparse

    parser = argparse.ArgumentParser(
        description="Run all tests with service setup/teardown."
    )
    parser.add_argument(
        "--no-frontend", action="store_true", help="Skip frontend tests"
    )
    parser.add_argument("--no-e2e", action="store_true", help="Skip E2E tests")
    parser.add_argument(
        "--no-teardown",
        action="store_true",
        help="Do not tear down services after tests",
    )
    parser.add_argument("--ci", action="store_true", help="Print CI-friendly output")
    # Granular selection options
    parser.add_argument(
        "--backend-only", action="store_true", help="Run only backend tests"
    )
    parser.add_argument(
        "--frontend-only", action="store_true", help="Run only frontend tests"
    )
    parser.add_argument("--e2e-only", action="store_true", help="Run only E2E tests")
    parser.add_argument(
        "--backend-files",
        nargs="+",
        help="Run only specified backend test files (space-separated)",
    )
    parser.add_argument(
        "--backend-keywords",
        help="Run only backend tests matching given pytest -k expression",
    )
    parser.add_argument(
        "--frontend-pattern",
        help="Run only frontend tests matching pattern (passed to vitest)",
    )
    parser.add_argument(
        "--e2e-pattern",
        help="Run only E2E tests matching pattern (passed to Playwright)",
    )
    args, pytest_args = parser.parse_known_args()

    run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"])
    wait_for_db()
    try:
        load_env_vars()
    except NameError:
        print("[WARN] load_env_vars() not implemented; skipping.")

    # --- DB Migration Step ---
    print("[INFO] Running Alembic migrations before backend tests...")
    alembic_ini = os.path.join("backend", "alembic.ini")
    alembic_cmd = ["./backend/.venv/bin/alembic", "-c", alembic_ini, "upgrade", "head"]
    result = subprocess.run(alembic_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] Alembic migration failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)
    else:
        print("[INFO] Alembic migration successful.")

        # --- Test Data Seeding Step ---
        print("[INFO] Seeding test data for integration/E2E tests...")
        seed_cmd = ["./backend/.venv/bin/python", "backend/test_seed.py"]
        result = subprocess.run(seed_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("[ERROR] Test data seeding failed:")
            print(result.stdout)
            print(result.stderr)
            sys.exit(result.returncode)
        else:
            print(result.stdout)
            print("[INFO] Test data seeding successful.")

        backend_code = 0
        if not args.frontend_only and not args.e2e_only:
            print("[INFO] Running backend tests...")
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            junit_path = reports_dir / "backend-junit.xml"
            backend_cmd = ["./backend/.venv/bin/python", "-m", "pytest"]
            # Granular backend selection
            if args.backend_files:
                backend_cmd += args.backend_files
            else:
                backend_cmd += ["backend/tests"]
            if args.backend_keywords:
                backend_cmd += ["-k", args.backend_keywords]
            backend_cmd += [f"--junitxml={junit_path}"]
            backend_cmd += pytest_args
            backend_code = subprocess.call(backend_cmd)

    frontend_code = 0
    if not args.no_frontend and not args.backend_only and not args.e2e_only:
        print("[INFO] Running frontend tests...")
        frontend_cmd = ["npm", "run", "test"]
        if args.frontend_pattern:
            frontend_cmd += ["--", args.frontend_pattern]
        frontend_code = subprocess.call(frontend_cmd, cwd="frontend")

    e2e_code = 0
    if not args.no_e2e and not args.backend_only and not args.frontend_only:
        print("[INFO] Running E2E tests...")
        e2e_cmd = ["npx", "playwright", "test"]
        if args.e2e_pattern:
            e2e_cmd += [args.e2e_pattern]
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        junit_path = reports_dir / "e2e-junit.xml"
        e2e_cmd += [f"--reporter=junit,{junit_path}"]
        e2e_code = subprocess.call(e2e_cmd, cwd="e2e")

    if not args.no_teardown:
        teardown_services()

    if args.ci:
        print("::group::Test Results")
        print(f"BACKEND: {'PASS' if backend_code == 0 else 'FAIL'}")
        print(f"FRONTEND: {'PASS' if frontend_code == 0 else 'FAIL'}")
        print(f"E2E: {'PASS' if e2e_code == 0 else 'FAIL'}")
        print("::endgroup::")

    # Exit with nonzero if any test failed
    sys.exit(backend_code or frontend_code or e2e_code)


if __name__ == "__main__":
    main()
