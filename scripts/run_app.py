import os
import sys
import subprocess
import argparse


import json
import shutil
import re
import time
import platform
import urllib.request
import glob


def validate_npm_dependencies():
    print(
        "[VALIDATE] Checking npm dependencies in frontend,\
          backend, and e2e ..."
    )
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    for subdir in ["frontend", "backend", "e2e"]:
        pkg_dir = os.path.join(base_dir, subdir)
        pkg_json = os.path.join(pkg_dir, "package.json")
        node_modules = os.path.join(pkg_dir, "node_modules")
        if os.path.exists(pkg_json):
            with open(pkg_json) as f:
                try:
                    data = json.load(f)
                    has_deps = bool(data.get("dependencies")) or bool(
                        data.get("devDependencies")
                    )
                except Exception as e:
                    print(
                        f"[ERROR] Could not parse package.json\
                        in {subdir}: {e}"
                    )
                    has_deps = False
            if has_deps:
                if not os.path.exists(node_modules):
                    print(
                        f"[ERROR] node_modules missing in {subdir}. "
                        f"Run 'npm install' in {subdir}."
                    )
                else:
                    print(f"[OK] node_modules present in {subdir}.")
            else:
                print(
                    f"[OK] No dependencies in {subdir},\
                    node_modules not required."
                )
        else:
            print(f"[SKIP] No package.json in {subdir}.")


def validate_npm_precommit_scripts():
    print(
        "[VALIDATE] Checking for pre-commit scripts in \
            frontend, backend, and e2e ..."
    )

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for subdir in ["frontend", "backend", "e2e"]:
        pkg_dir = os.path.join(base_dir, subdir)
        pkg_json = os.path.join(pkg_dir, "package.json")
        if os.path.exists(pkg_json):
            with open(pkg_json) as f:
                try:
                    data = json.load(f)
                    scripts = data.get("scripts", {})
                    if "pre-commit" in scripts:
                        print(f"[OK] pre-commit script found in {subdir}.")
                    else:
                        print(
                            f"[ERROR] pre-commit script missing \
                            in {subdir}."
                        )
                except Exception as e:
                    print(
                        f"[ERROR] Could not parse package.json\
                        in {subdir}: {e}"
                    )
        else:
            print(f"[SKIP] No package.json in {subdir}.")


def validate_processes():
    print(
        "[VALIDATE] Checking for required processes\
            (docker, docker compose, node, npm, python3.12) ..."
    )

    required = ["docker", "docker-compose", "node", "npm", "python3.12"]
    for proc in required:
        if shutil.which(proc):
            print(f"[OK] {proc} is available.")
        else:
            print(f"[ERROR] {proc} is missing from PATH.")


def setup_npm_dependencies():
    print(
        "\n[STEP 1.5] Installing npm dependencies for \
        frontend, backend, and e2e ..."
    )
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for subdir in ["frontend", "backend", "e2e"]:
        pkg_dir = os.path.join(base_dir, subdir)
        pkg_json = os.path.join(pkg_dir, "package.json")
        if os.path.exists(pkg_json):
            print(f"[INFO] Running 'npm install' in {subdir} ...")
            result = subprocess.run(["npm", "install"], cwd=pkg_dir)
            if result.returncode == 0:
                print(f"[OK] npm dependencies installed in {subdir}.")
            else:
                print(
                    f"[ERROR] npm install failed \
                    in {subdir}. Please check the logs."
                )
        else:
            print(
                f"[SKIP] No package.json found \
                in {subdir}, skipping npm install."
            )


def cleanup_orphans():
    # Remove orphaned containers not managed by current compose file
    print("[STEP] Cleaning up orphaned containers...")
    result = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            "name=anantam501-url-proxy",
            "--format",
            "{{.ID}}",
        ],
        capture_output=True,
        text=True,
    )
    orphan_id = result.stdout.strip()
    if orphan_id:
        subprocess.run(["docker", "rm", "-f", orphan_id])
        print(f"[OK] Orphaned container removed: {orphan_id}")
    else:
        print("[OK] No orphaned containers found.")


def bring_app_live():
    print("[STEP] Bringing up the application stack (live mode)...")
    infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "infra"))
    subprocess.run(["docker", "compose", "up"], cwd=infra_dir)


def build_images():
    print("[STEP] Building all Docker images (no cache)...")
    infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "infra"))
    subprocess.run(["docker", "compose", "build", "--no-cache"], cwd=infra_dir)


def check_env_file_and_vars():
    print("[STEP 3] Checking .env file and required variables...")

    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    required_vars = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
    if not os.path.exists(env_path):
        print(
            f"[FATAL] .env file not found at {env_path}. "
            "Please create it with required variables."
        )
        sys.exit(1)
    with open(env_path) as f:
        env_content = f.read()
    missing = []
    for var in required_vars:
        if not re.search(rf"^{var}=.+", env_content, re.MULTILINE):
            missing.append(var)
    if missing:
        print(
            f"[FATAL] The following required variables are \
                missing in .env: "
            f"{', '.join(missing)}"
        )
        sys.exit(1)
    print("[OK] .env file and required variables are present.")


def test_docker_compose_stack():
    print("[STEP 4] Testing Docker Compose stack startup...")

    infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "infra"))
    # Copy .env to infra if not present
    env_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    env_dst = os.path.join(infra_dir, ".env")
    if not os.path.exists(env_dst):
        import shutil

        shutil.copy(env_src, env_dst)
        print(f"[INFO] Copied .env to {env_dst} for Docker Compose.")
    # Start stack
    result = subprocess.run(["docker", "compose", "up", "-d"], cwd=infra_dir)
    if result.returncode != 0:
        print(
            "[FATAL] Failed to start Docker Compose stack. "
            "Check docker-compose.yml and .env."
        )
        sys.exit(1)
    print(
        "[OK] Docker Compose stack started. Waiting for\
        services to initialize..."
    )
    time.sleep(5)
    # Check container health (basic)
    ps = subprocess.run(
        ["docker", "compose", "ps"],
        cwd=infra_dir,
        capture_output=True,
        text=True,
    )
    print(ps.stdout)
    # Stop stack after test
    subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
    print("[OK] Docker Compose stack stopped after test.")


def ensure_homebrew_path_in_shell():
    print("[STEP 0.1] Ensuring Homebrew bin directory is in your PATH...")

    home = os.path.expanduser("~")
    shell_rc = os.path.join(home, ".zshrc")
    # Determine Homebrew bin path based on architecture
    brew_bin = (
        "/opt/homebrew/bin" if platform.machine() == "arm64" else "/usr/local/bin"
    )
    current_path = os.environ.get("PATH", "")
    if brew_bin not in current_path:
        print(
            f"[INFO] {brew_bin} not found in PATH. "
            f"Attempting to add to {shell_rc} ..."
        )
        export_line = (
            f"\n# Added by Anantam setup script for Homebrew\n"
            f'export PATH="{brew_bin}:$PATH"\n'
        )
        try:
            with open(shell_rc, "a") as f:
                f.write(export_line)
            print(
                f"[OK] Added {brew_bin} to {shell_rc}. "
                "Please restart your terminal or run 'source {shell_rc}' \
                    to apply changes."
            )
        except Exception as e:
            print(f"[ERROR] Could not update {shell_rc}: {e}")
    else:
        print(f"[OK] {brew_bin} is already in your PATH.")


def check_and_install_docker_compose_plugin():
    print("[STEP 0] Checking for Docker Compose plugin (docker compose)...")
    result = subprocess.run(
        ["docker", "compose", "version"], capture_output=True, text=True
    )
    if result.returncode == 0:
        print("[OK] Docker Compose plugin is already installed.")
        return
    print(
        "[WARN] Docker Compose plugin not found or not working. "
        "Attempting to install the official plugin..."
    )

    arch = platform.machine()
    cli_plugins_dir = os.path.expanduser("~/.docker/cli-plugins")
    os.makedirs(cli_plugins_dir, exist_ok=True)
    # Fetch latest release version from GitHub API
    api_url = "https://api.github.com/repos/docker/compose/releases/latest"
    try:
        with urllib.request.urlopen(api_url) as resp:
            release_data = json.load(resp)
            tag_name = release_data["tag_name"]
    except Exception as e:
        print(
            f"[FATAL] Could not fetch latest Docker \
            Compose release info: {e}"
        )
        sys.exit(1)
    dest = os.path.join(cli_plugins_dir, "docker-compose")
    bin_names = []
    if arch == "arm64":
        bin_names = [
            "docker-compose-darwin-aarch64",
            "docker-compose-darwin-arm64",
        ]
    else:
        bin_names = ["docker-compose-darwin-x86_64"]
    success = False
    for bin_name in bin_names:
        url = (
            f"https://github.com/docker/compose/releases/download/{tag_name}/"
            f"{bin_name}"
        )
        print(
            f"[INFO] Attempting to download Docker \
            Compose plugin from {url} ..."
        )
        try:
            urllib.request.urlretrieve(url, dest)
            os.chmod(dest, 0o755)
            print(
                f"[OK] Docker Compose plugin downloaded to {dest} and made executable."
            )
            success = True
            break
        except Exception as e:
            print(f"[WARN] Failed to download {bin_name}: {e}")
    if not success:
        print(
            "[FATAL] Could not download a compatible \
                Docker Compose plugin for your system. "
            "Please check the latest release assets \
                at https://github.com/docker/compose/releases \
                    and install manually if needed."
        )
        sys.exit(1)
    # Re-check if docker compose is now available
    result2 = subprocess.run(
        ["docker", "compose", "version"], capture_output=True, text=True
    )
    if result2.returncode == 0:
        print("[OK] Docker Compose plugin is now installed and working.")
        return
    print(
        "[FATAL] Docker Compose plugin is still not \
            available after plugin install. "
        "Please check your Docker installation and PATH."
    )
    sys.exit(1)


SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
VALIDATE_ENV_SCRIPT = os.path.join(SCRIPTS_DIR, "validate_environment.py")


def run_env_validation(use_venv_python=False):
    print("\n[STEP 1] Validating environment...")
    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    )
    venv_python = os.path.join(backend_dir, ".venv", "bin", "python")
    if use_venv_python and os.path.exists(venv_python):
        result = subprocess.run([venv_python, VALIDATE_ENV_SCRIPT])
    else:
        result = subprocess.run([sys.executable, VALIDATE_ENV_SCRIPT])
    if result.returncode != 0:
        print("[FATAL] Environment validation failed. Exiting.")
        sys.exit(1)
    print("[OK] Environment validation passed.\n")


def setup_python_venv():
    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    )
    venv_dir = os.path.join(backend_dir, ".venv")
    requirements = os.path.join(backend_dir, "requirements.txt")
    print(
        f"\n[STEP 2] Setting up Python 3.12 virtual \
        environment in {venv_dir} ..."
    )
    if not os.path.exists(venv_dir):
        result = subprocess.run(["python3.12", "-m", "venv", venv_dir])
        if result.returncode != 0:
            print("[FATAL] Failed to create virtual environment. Exiting.")
            sys.exit(1)
        print("[OK] Virtual environment created.")
    else:
        print("[OK] Virtual environment already exists.")
    pip_path = os.path.join(venv_dir, "bin", "pip")
    print(f"[STEP 2.1] Installing requirements from {requirements} ...")
    result = subprocess.run([pip_path, "install", "-r", requirements])
    if result.returncode != 0:
        print("[FATAL] Failed to install requirements. Exiting.")
        sys.exit(1)
    print("[OK] Requirements installed.")
    print("[STEP 2.2] Validating installed packages ...")
    result = subprocess.run([pip_path, "check"])
    if result.returncode == 0:
        print("[OK] All required Python packages are installed and valid.")
    else:
        print(
            "[ERROR] Some Python packages are missing or \
                incompatible. Please check requirements.txt."
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Anantam Master Control Script")
    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Bring up the application stack and keep it \
                running "
            "(docker compose up)"
        ),
    )
    parser.add_argument(
        "--tests",
        action="store_true",
        help=(
            "Run all backend test suites with stack up, \
            then stop stack"
        ),
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Rebuild all Docker images with no cache",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove all containers, volumes, and orphans",
    )
    args = parser.parse_args()

    print("\n=== Master Control Application Execution Script ===\n")
    ensure_homebrew_path_in_shell()
    check_and_install_docker_compose_plugin()
    validate_processes()
    setup_npm_dependencies()
    validate_npm_dependencies()
    validate_npm_precommit_scripts()

    if args.cleanup:
        infra_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "infra")
        )
        subprocess.run(["docker", "compose", "down", "-v"], cwd=infra_dir)
        cleanup_orphans()
        print("[OK] Cleanup complete.")
        return

    if args.build:
        build_images()
        print("[OK] Build complete.")
        return

    if args.live:
        bring_app_live()
        return

    if args.tests:
        # Start stack (detached)
        print(
            "[STEP] Starting Docker Compose stack \
            for test suites ..."
        )
        infra_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "infra")
        )
        env_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        env_dst = os.path.join(infra_dir, ".env")
        if not os.path.exists(env_dst):
            import shutil

            shutil.copy(env_src, env_dst)
            print(f"[INFO] Copied .env to {env_dst} for Docker Compose.")
        result = subprocess.run(["docker", "compose", "up", "-d"], cwd=infra_dir)
        if result.returncode != 0:
            print(
                "[FATAL] Failed to start Docker Compose stack. \
                    Check docker-compose.yml and .env."
            )
            sys.exit(1)
        import time
        import urllib.request

        # Wait for backend to be healthy by curling the endpoint
        print(
            "[STEP] Waiting for backend service \
            to be healthy (curl check) ..."
        )
        healthy = False
        for _ in range(30):
            try:
                with urllib.request.urlopen(
                    "http://localhost:8000/", timeout=2
                ) as resp:
                    if resp.status == 200:
                        healthy = True
                        print("[OK] Backend is healthy.")
                        break
            except Exception:
                pass
            time.sleep(2)
        if not healthy:
            print("[FATAL] Backend did not become healthy in time.")
            subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
            sys.exit(1)

        # Run Alembic migrations inside backend container
        print("[STEP] Running Alembic migrations in backend container ...")
        print("[DEBUG] infra_dir: {}".format(infra_dir))
        print("[DEBUG] Current working directory: {}".format(os.getcwd()))
        print("[DEBUG] Environment: {}".format(os.environ))
        # Use 'docker compose ps -q backend' to get the backend container ID
        try:
            ps = subprocess.run(
                ["docker", "compose", "ps", "-q", "backend"],
                cwd=infra_dir,
                capture_output=True,
                text=True,
            )
            backend_container_id = ps.stdout.strip()
        except Exception as e:
            print(f"[WARN] Could not determine backend container ID: {e}")
            backend_container_id = None
        if not backend_container_id:
            print(
                "[FATAL] Could not determine backend container ID. \
                    Alembic migration cannot proceed."
            )
            subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
            sys.exit(1)
            print(
                f"[DEBUG] Using backend container ID: \
                {backend_container_id}"
            )
        if backend_container_id:
            # Debug: List /app and show alembic.ini \
            # contents before running Alembic
            print("[DEBUG] Listing /app directory in backend container:")
            subprocess.run(
                ["docker", "compose", "exec", "-T", "backend", "sh", "-c", "ls -l /app"]
            )
            print(
                "[DEBUG] Showing contents of /app/alembic.ini \
                in backend container:"
            )
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "backend",
                    "sh",
                    "-c",
                    "cat /app/alembic.ini",
                ]
            )
            print(
                "[DEBUG] Checking Alembic availability in \
                backend container:"
            )
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "backend",
                    "sh",
                    "-c",
                    "alembic --help",
                ]
            )
            # Check if /app/alembic.ini exists in the backend container
            check_ini_cmd = [
                "docker",
                "compose",
                "exec",
                "-T",
                "backend",
                "sh",
                "-c",
                "ls /app/alembic.ini",
            ]
            ini_result = subprocess.run(check_ini_cmd, capture_output=True, text=True)
            if ini_result.returncode != 0:
                print(
                    "[FATAL] /app/alembic.ini not found in backend container. "
                    "Alembic migration cannot proceed."
                )
                print(ini_result.stdout)
                print(ini_result.stderr)
                subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
                sys.exit(1)
            alembic_cmd = [
                "docker",
                "compose",
                "exec",
                "-T",
                "backend",
                "sh",
                "-c",
                "cd /app && alembic -c /app/alembic.ini upgrade head",
            ]
            result = subprocess.run(alembic_cmd)
            if result.returncode == 0:
                print("[OK] Alembic migrations applied.")
            else:
                print("[FATAL] Alembic migrations failed. See output above.")
                subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
                sys.exit(1)
        else:
            print(
                "[FATAL] Could not find backend container to \
                run Alembic migrations."
            )
            subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
            sys.exit(1)

        # Run all test scripts in tests/
        print("[STEP] Running all backend test suites ...")
        backend_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "backend")
        )
        venv_python = os.path.join(backend_dir, ".venv", "bin", "python")
        tests_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "tests")
        )

        test_files = sorted(glob.glob(os.path.join(tests_dir, "test_*.py")))
        all_passed = True
        for test_script in test_files:
            print(f"[TEST] Running {os.path.basename(test_script)} ...")
            result = subprocess.run([venv_python, test_script])
            if result.returncode == 0:
                print(f"[OK] {os.path.basename(test_script)} passed.")
            else:
                print(
                    f"[FAIL] {os.path.basename(test_script)} failed. \
                        See output above."
                )
                all_passed = False
        # Stop stack after tests
        print("[STEP] Stopping Docker Compose stack after tests ...")
        subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
        if all_passed:
            print("[OK] All backend test suites passed.")
        else:
            print("[FAIL] Some backend test suites failed.")
        return

    # Default: full validation, stack up, test, stack down

    # Initial environment validation (tools, versions, etc.)
    run_env_validation()
    # Setup Python venv and install requirements
    setup_python_venv()
    # Re-run environment validation using backend venv \
    # Python to check for missing packages after install
    run_env_validation(use_venv_python=True)
    check_env_file_and_vars()

    # Start stack (in detached mode)
    print("[STEP 4] Starting Docker Compose stack for testing ...")
    infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "infra"))
    env_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    env_dst = os.path.join(infra_dir, ".env")
    if not os.path.exists(env_dst):
        import shutil

        shutil.copy(env_src, env_dst)
        print(f"[INFO] Copied .env to {env_dst} for Docker Compose.")
    result = subprocess.run(["docker", "compose", "up", "-d"], cwd=infra_dir)
    if result.returncode != 0:
        print(
            "[FATAL] Failed to start Docker Compose stack. \
                Check docker-compose.yml and .env."
        )
        sys.exit(1)
    import time

    # Wait for backend to be healthy
    print("[STEP 4.1] Waiting for backend service to be healthy ...")
    healthy = False
    for _ in range(30):
        ps = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=infra_dir,
            capture_output=True,
            text=True,
        )
        try:
            services = json.loads(ps.stdout)
            for svc in services:
                if svc.get("Service") == "backend" and "healthy" in svc.get(
                    "Status", ""
                ):
                    healthy = True
                    break
        except Exception:
            pass
        if healthy:
            print("[OK] Backend is healthy.")
            break
        time.sleep(2)
    if not healthy:
        print("[FATAL] Backend did not become healthy in time.")
        subprocess.run(["docker", "compose", "down"], cwd=infra_dir)
        sys.exit(1)

    # Run automated tests
    print("[STEP 5] Running automated backend tests ...")
    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    )
    venv_python = os.path.join(backend_dir, ".venv", "bin", "python")
    tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests"))
    test_script = os.path.join(tests_dir, "test_auth.py")
    if os.path.exists(test_script):
        result = subprocess.run([venv_python, test_script])
        if result.returncode == 0:
            print("[OK] Authentication endpoints passed automated tests.")
        else:
            print(
                "[FAIL] Authentication endpoints failed \
                    automated tests. See output above."
            )
    else:
        print(f"[WARN] Test script not found: {test_script}")

    # Stop stack after tests
    print("[STEP 6] Stopping Docker Compose stack after tests ...")
    subprocess.run(["docker", "compose", "down"], cwd=infra_dir)

    print(
        "[INFO] All initial checks, stack test, \
            and automated tests complete. \
                Use --live to keep the app running."
    )


if __name__ == "__main__":
    main()
