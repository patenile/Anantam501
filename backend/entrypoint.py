#!/usr/bin/env python3
import os
import sys


ALEMBIC_INI = "/app/alembic.ini"
MIGRATIONS_DIR = "/app/migrations"

if not os.path.isfile(ALEMBIC_INI):
    print(f"[FATAL] {ALEMBIC_INI} is missing!", file=sys.stderr)
    sys.exit(1)
if not os.path.isdir(MIGRATIONS_DIR):
    print(f"[FATAL] {MIGRATIONS_DIR} directory is missing!", file=sys.stderr)
    sys.exit(1)

# Pass through to the actual command
if len(sys.argv) > 1:
    os.execvp(sys.argv[1], sys.argv[1:])
else:
    print("[FATAL] No command provided to entrypoint.", file=sys.stderr)
    sys.exit(1)
