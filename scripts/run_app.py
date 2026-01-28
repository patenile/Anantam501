import argparse
def cleanup_orphans():
    # Remove orphaned containers not managed by current compose file
    import subprocess
    print("[STEP] Cleaning up orphaned containers...")
    result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=anantam501-url-proxy', '--format', '{{.ID}}'], capture_output=True, text=True)
    orphan_id = result.stdout.strip()
    if orphan_id:
        subprocess.run(['docker', 'rm', '-f', orphan_id])
        print(f"[OK] Orphaned container removed: {orphan_id}")
    else:
        print("[OK] No orphaned containers found.")
def bring_app_live():
    print("[STEP] Bringing up the application stack (live mode)...")
    infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra'))
    subprocess.run(['docker', 'compose', 'up'], cwd=infra_dir)
def build_images():
    print("[STEP] Building all Docker images (no cache)...")
    infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra'))
    subprocess.run(['docker', 'compose', 'build', '--no-cache'], cwd=infra_dir)
def check_env_file_and_vars():
    print("[STEP 3] Checking .env file and required variables...")
    import re
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    required_vars = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
    if not os.path.exists(env_path):
        print(f"[FATAL] .env file not found at {env_path}. Please create it with required variables.")
        sys.exit(1)
    with open(env_path) as f:
        env_content = f.read()
    missing = []
    for var in required_vars:
        if not re.search(rf'^{var}=.+', env_content, re.MULTILINE):
            missing.append(var)
    if missing:
        print(f"[FATAL] The following required variables are missing in .env: {', '.join(missing)}")
        sys.exit(1)
    print("[OK] .env file and required variables are present.")

def test_docker_compose_stack():
    print("[STEP 4] Testing Docker Compose stack startup...")
    import time
    infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra'))
    # Copy .env to infra if not present
    env_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    env_dst = os.path.join(infra_dir, '.env')
    if not os.path.exists(env_dst):
        import shutil
        shutil.copy(env_src, env_dst)
        print(f"[INFO] Copied .env to {env_dst} for Docker Compose.")
    # Start stack
    result = subprocess.run(['docker', 'compose', 'up', '-d'], cwd=infra_dir)
    if result.returncode != 0:
        print("[FATAL] Failed to start Docker Compose stack. Check docker-compose.yml and .env.")
        sys.exit(1)
    print("[OK] Docker Compose stack started. Waiting for services to initialize...")
    time.sleep(5)
    # Check container health (basic)
    ps = subprocess.run(['docker', 'compose', 'ps'], cwd=infra_dir, capture_output=True, text=True)
    print(ps.stdout)
    # Stop stack after test
    subprocess.run(['docker', 'compose', 'down'], cwd=infra_dir)
    print("[OK] Docker Compose stack stopped after test.")
def ensure_homebrew_path_in_shell():
    print("[STEP 0.1] Ensuring Homebrew bin directory is in your PATH...")
    import platform
    home = os.path.expanduser("~")
    shell_rc = os.path.join(home, ".zshrc")
    # Determine Homebrew bin path based on architecture
    brew_bin = "/opt/homebrew/bin" if platform.machine() == "arm64" else "/usr/local/bin"
    current_path = os.environ.get("PATH", "")
    if brew_bin not in current_path:
        print(f"[INFO] {brew_bin} not found in PATH. Attempting to add to {shell_rc} ...")
        export_line = f'\n# Added by Anantam setup script for Homebrew\nexport PATH=\"{brew_bin}:$PATH\"\n'
        try:
            with open(shell_rc, "a") as f:
                f.write(export_line)
            print(f"[OK] Added {brew_bin} to {shell_rc}. Please restart your terminal or run 'source {shell_rc}' to apply changes.")
        except Exception as e:
            print(f"[ERROR] Could not update {shell_rc}: {e}")
    else:
        print(f"[OK] {brew_bin} is already in your PATH.")
def check_and_install_docker_compose_plugin():
    print("[STEP 0] Checking for Docker Compose plugin (docker compose)...")
    result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] Docker Compose plugin is already installed.")
        return
    print("[WARN] Docker Compose plugin not found or not working. Attempting to install the official plugin...")
    import platform
    import json
    import urllib.request
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
        print(f"[FATAL] Could not fetch latest Docker Compose release info: {e}")
        sys.exit(1)
    dest = os.path.join(cli_plugins_dir, "docker-compose")
    bin_names = []
    if arch == "arm64":
        bin_names = ["docker-compose-darwin-aarch64", "docker-compose-darwin-arm64"]
    else:
        bin_names = ["docker-compose-darwin-x86_64"]
    success = False
    for bin_name in bin_names:
        url = f"https://github.com/docker/compose/releases/download/{tag_name}/{bin_name}"
        print(f"[INFO] Attempting to download Docker Compose plugin from {url} ...")
        try:
            urllib.request.urlretrieve(url, dest)
            os.chmod(dest, 0o755)
            print(f"[OK] Docker Compose plugin downloaded to {dest} and made executable.")
            success = True
            break
        except Exception as e:
            print(f"[WARN] Failed to download {bin_name}: {e}")
    if not success:
        print(f"[FATAL] Could not download a compatible Docker Compose plugin for your system. Please check the latest release assets at https://github.com/docker/compose/releases and install manually if needed.")
        sys.exit(1)
    # Re-check if docker compose is now available
    result2 = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
    if result2.returncode == 0:
        print("[OK] Docker Compose plugin is now installed and working.")
        return
    print("[FATAL] Docker Compose plugin is still not available after plugin install. Please check your Docker installation and PATH.")
    sys.exit(1)
import subprocess
import sys
import os

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
VALIDATE_ENV_SCRIPT = os.path.join(SCRIPTS_DIR, 'validate_environment.py')


def run_env_validation():
    print("\n[STEP 1] Validating environment...")
    result = subprocess.run([sys.executable, VALIDATE_ENV_SCRIPT])
    if result.returncode != 0:
        print("[FATAL] Environment validation failed. Exiting.")
        sys.exit(1)
    print("[OK] Environment validation passed.\n")


def setup_python_venv():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    venv_dir = os.path.join(backend_dir, '.venv')
    requirements = os.path.join(backend_dir, 'requirements.txt')
    print(f"\n[STEP 2] Setting up Python 3.12 virtual environment in {venv_dir} ...")
    if not os.path.exists(venv_dir):
        result = subprocess.run(['python3.12', '-m', 'venv', venv_dir])
        if result.returncode != 0:
            print("[FATAL] Failed to create virtual environment. Exiting.")
            sys.exit(1)
        print("[OK] Virtual environment created.")
    else:
        print("[OK] Virtual environment already exists.")
    pip_path = os.path.join(venv_dir, 'bin', 'pip')
    print(f"[STEP 2.1] Installing requirements from {requirements} ...")
    result = subprocess.run([pip_path, 'install', '-r', requirements])
    if result.returncode != 0:
        print("[FATAL] Failed to install requirements. Exiting.")
        sys.exit(1)
    print("[OK] Requirements installed.")
    print("[STEP 2.2] Validating installed packages ...")
    result = subprocess.run([pip_path, 'check'])
    if result.returncode == 0:
        print("[OK] All required Python packages are installed and valid.")
    else:
        print("[ERROR] Some Python packages are missing or incompatible. Please check requirements.txt.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Anantam Master Control Script")
    parser.add_argument('--live', action='store_true', help='Bring up the application stack and keep it running (docker compose up)')
    parser.add_argument('--build', action='store_true', help='Rebuild all Docker images with no cache')
    parser.add_argument('--cleanup', action='store_true', help='Remove all containers, volumes, and orphans')
    args = parser.parse_args()

    print("\n=== Master Control Application Execution Script ===\n")
    ensure_homebrew_path_in_shell()
    check_and_install_docker_compose_plugin()

    if args.cleanup:
        infra_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'infra'))
        subprocess.run(['docker', 'compose', 'down', '-v'], cwd=infra_dir)
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

    # Default: full validation and stack test
    run_env_validation()
    setup_python_venv()
    check_env_file_and_vars()
    test_docker_compose_stack()
    print("[INFO] All initial checks and stack test complete. Use --live to keep the app running.")

if __name__ == "__main__":
    main()
