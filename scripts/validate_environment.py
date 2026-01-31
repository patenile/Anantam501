# ...existing code...
import shutil
import subprocess

REQUIRED_TOOLS = {
    "python3.12": "Python 3.12",
    "node": "Node.js",
    "docker": "Docker",
    "docker compose": "Docker Compose (plugin)",
    "colima": "Colima (for macOS)",
}

# Minimum required versions
MIN_VERSIONS = {
    "python3.12": (3, 12),
    "node": (18, 0),
    "docker": (20, 10),
    "docker compose": (2, 24),  # Compose plugin v2.24+ for watch support
    "colima": (0, 5),
}


def check_tool(tool, display_name):
    if tool == "docker compose":
        # Check if 'docker compose' subcommand works
        try:
            result = subprocess.run(
                ["docker", "compose", "version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"[OK] {display_name} is available as a Docker subcommand.")
                return True
            else:
                print(
                    f"[ERROR] {display_name} not found or not working as a "
                    f"Docker subcommand."
                )
                return False
        except Exception as e:
            print(f"[ERROR] {display_name} check failed: {e}")
            return False
    else:
        path = shutil.which(tool)
        if not path:
            print(f"[ERROR] {display_name} not found in PATH.")
            return False
        print(f"[OK] {display_name} found: {path}")
        return True


def get_version(tool, version_arg="--version"):
    try:
        if tool == "docker compose":
            result = subprocess.run(
                ["docker", "compose", "version"], capture_output=True, text=True
            )
            return result.stdout.strip() or result.stderr.strip()
        else:
            result = subprocess.run([tool, version_arg], capture_output=True, text=True)
            return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return str(e)


def parse_version(version_str):
    import re

    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", version_str)
    if match:
        return tuple(int(x) for x in match.groups() if x is not None)
    return ()


def check_version(tool, min_version):
    version_str = get_version(tool)
    version_tuple = parse_version(version_str)
    if not version_tuple:
        print(f"[WARN] Could not parse version for {tool}: {version_str}")
        return False
    if version_tuple >= min_version:
        print(f"[OK] {tool} version {version_tuple} >= {min_version}")
        return True
    else:
        print(f"[ERROR] {tool} version {version_tuple} < {min_version}")
        return False


def main():
    print("\n=== Environment Validation Script ===\n")
    all_ok = True
    for tool, display_name in REQUIRED_TOOLS.items():
        ok = check_tool(tool, display_name)
        if ok and tool in MIN_VERSIONS:
            ok = check_version(tool, MIN_VERSIONS[tool])
        all_ok = all_ok and ok

    # Python package checks (backend/.venv)
    print("\n[STEP] Checking required Python packages in backend/.venv ...")
    import os

    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    )
    venv_python = os.path.join(backend_dir, ".venv", "bin", "python")
    required_pkgs = [
        "fastapi",
        "uvicorn",
        "psycopg2-binary",
        "sqlalchemy",
        "python-dotenv",
        "passlib",
        "python-jose",
        "python-multipart",
        "fastapi-pagination",
        "aiofiles",
        "aiosmtplib",
        "alembic",
        "loguru",
    ]
    missing_pkgs = []
    for pkg in required_pkgs:
        result = subprocess.run(
            [
                venv_python,
                "-c",
                f'import {pkg.replace("-", "_")}',
            ],
            capture_output=True,
        )
        if result.returncode != 0:
            missing_pkgs.append(pkg)
    if not missing_pkgs:
        print("[OK] All required Python packages are installed in backend/.venv.")
    else:
        print(
            f"[ERROR] Missing Python packages in backend/.venv: "
            f"{', '.join(missing_pkgs)}"
        )
        all_ok = False

    if all_ok:
        print(
            "\n[ALL OK] All required tools and Python packages are installed "
            "and meet minimum version requirements."
        )
    else:
        print(
            "\n[FAIL] Some required tools or Python packages are \
                missing or do not meet "
            "version requirements. Please install or upgrade\
                them before proceeding."
        )
    print("\nValidation complete.\n")


if __name__ == "__main__":
    main()
