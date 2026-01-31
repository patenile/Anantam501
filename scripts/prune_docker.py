#!/usr/bin/env python3
"""
prune_docker.py: Maintenance script to prune unused Docker volumes and networks.

- Removes dangling (unused) Docker volumes
- Removes unused Docker networks (not in use by any container)
- Prints a summary of reclaimed space
- Safe: does not remove in-use resources

Usage:
    python scripts/prune_docker.py
    # or, if executable:
    ./scripts/prune_docker.py

Requires Docker CLI to be installed and available in PATH.
"""
import subprocess
import sys


def run(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return e.returncode


def main():
    print("\033[1;34m[INFO]\033[0m Pruning unused Docker volumes...")
    run("docker volume prune -f")
    print("\033[1;34m[INFO]\033[0m Pruning unused Docker networks...")
    run("docker network prune -f")
    print("\033[1;32m[SUCCESS]\033[0m Docker maintenance complete.")


if __name__ == "__main__":
    main()
