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
