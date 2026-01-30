# Anantam Home Interior Design Collaboration App

![CI/CD](https://github.com/${{ github.repository }}/actions/workflows/ci-cd.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-auto--generated-brightgreen)

## Project Overview
A collaborative platform for home interior design, featuring modular architecture, AI integration, and robust local development with Docker Compose and Nginx reverse proxy.

## Quick Start

1. **Clone the repository**
2. **Create your .env file**
	- Copy the provided .env template and adjust values as needed.
3. **Run the master control script**
	- `python3 scripts/run_app.py`
4. **Build and start all services**
	 - `cd infra && docker compose up`
	 - For live-reload during development, use:
		 - `docker compose watch`
		 - (Requires Docker Compose plugin v2.24+ and compose.watch.yml)

## Docker Compose Plugin Installation (macOS)

If you see an error about `docker compose` not being found, you have two options:

1. **Recommended:** Install or update [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/). It includes the Docker Compose plugin by default.

2. **Manual (no Docker Desktop):**
	 - Download and install the official Docker Compose plugin:
		 ```sh
		 mkdir -p ~/.docker/cli-plugins
		 # For Apple Silicon (M1/M2/arm64):
		 curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-darwin-arm64 -o ~/.docker/cli-plugins/docker-compose
		 # For Intel Macs (x86_64):
		 curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-darwin-x86_64 -o ~/.docker/cli-plugins/docker-compose
		 chmod +x ~/.docker/cli-plugins/docker-compose
		 ```

Or simply run the master control script (`python3 scripts/run_app.py`), which will attempt to install the correct plugin for you automatically.
5. **Access the app**
	- Open [http://localhost](http://localhost) in your browser.

## .env File Example
```
POSTGRES_USER=anantam
POSTGRES_PASSWORD=supersecret
POSTGRES_DB=anantam_db
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://anantam:supersecret@db:5432/anantam_db
REACT_APP_API_BASE_URL=/api
```

## Architecture
- **Nginx**: Reverse proxy, routes /api to backend and all other traffic to frontend, exposes only port 80.
- **Backend**: FastAPI, connects to PostgreSQL using DATABASE_URL from .env.
- **Frontend**: React (Vite/Next.js), makes API calls to /api (handled by Nginx).
- **PostgreSQL**: Database service, credentials and DB name from .env.

## Development Notes
- All configuration is managed via the .env file at the project root.
- Docker Compose (plugin) orchestrates all services; health checks and network aliases ensure robust startup.
- For live-reload, use compose.watch.yml and run `docker compose watch` in the infra directory.
- For remote/local access, open port 80 on your host machine.
- No cloud resources required; everything runs locally.

## Security
- Do not commit your real .env file with secrets to version control.
- For production, add HTTPS and further harden Nginx as needed.

## Further Reading
- See docs/development_flow.md for detailed architecture and workflow.
# Anantam501
This application is for keeping the very organised discussion over the working interior design project
