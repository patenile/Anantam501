## 6. Advanced Docker Compose Enhancements

- **Resource Limits**: Each service has CPU and memory limits to prevent resource exhaustion and ensure fair usage.
- **Restart Policy**: Services use `restart: unless-stopped` for resilience, so they automatically restart on failure or system reboot.
- **Centralized Logging**: All services use the json-file log driver with rotation, making logs accessible and preventing disk overuse.
- **Network Isolation**: Backend, frontend, and database services are further isolated with dedicated networks, improving security and reducing cross-service noise.
- **Production Readiness**: These enhancements make the stack more robust, easier to monitor, and safer for scaling or future cloud migration.

These improvements ensure your application is resilient, secure, and ready for advanced development and deployment scenarios.
## 5. System Dark/Light Mode Compatibility

- **Requirement**: The application frontend must fully support system dark and light mode preferences, adapting its appearance automatically based on the user's OS or browser settings.
- **Technologies**:
  - Use CSS custom properties (variables) and media queries (prefers-color-scheme) for theme switching.
  - Leverage a design system or UI library with built-in dark/light mode support (e.g., Material UI, Chakra UI, Tailwind CSS, or custom solution).
  - Ensure all custom components and styles respect the theme context.
  - Test across major browsers and operating systems for consistent appearance.

This ensures a modern, accessible, and user-friendly experience for all users.
## 4. Version Control, Commit Checks, and Post-Process Automation

- **Version Control**: All code must be managed in a Git repository with a clear branching strategy (e.g., main, develop, feature branches).
- **Commit Message Standards**: Use conventional commit messages for clarity and automation (e.g., feat:, fix:, docs:).
- **Pre-Commit Hooks**: Enforce code formatting and linting before commits using pre-commit hooks:
  - Python: black, isort, flake8
  - JavaScript/TypeScript: prettier, eslint
- **Pre-Push Hooks**: Require all tests to pass before allowing code to be pushed.
- **Dependency Checks**: Automate vulnerability checks (e.g., pip-audit, npm audit, Dependabot).
- **Automated Code Review**: Use CI (e.g., GitHub Actions) to run builds, tests, and linting on every pull request.
- **Automated Deployment**: Deploy to staging or production automatically after successful checks, as defined in CI/CD pipeline.
- **Database Backups & Monitoring**: Schedule regular database backups and health monitoring as part of post-deployment processes.

This ensures code quality, security, and operational reliability throughout the development lifecycle.
# Development Flow Document

## 1. Professional Task List for Application Development

1. Scaffold project directory structure
2. Install and validate all required tools and dependencies (Python 3.12, Node.js, Docker, Docker Compose, etc.)
3. Set up Docker Compose (plugin) for backend, frontend, and database
  - Use `docker compose` (not legacy `docker-compose`).
  - For live-reload during development, use `docker compose watch` with compose.watch.yml.
4. Validate Docker, backend, frontend, and database setup (ensure all services are running and accessible)
5. Initialize Python backend with FastAPI and .venv
6. Initialize React frontend with Vite or Next.js
7. Add PostgreSQL service and configure database connection
8. Perform PostgreSQL initial setup (create database, tables, fields) and health checks
9. Implement user authentication (JWT/OAuth)
10. Design and implement core data models (User, Home, Room, etc.)
11. Set up backend API endpoints for CRUD operations
12. Implement frontend UI for core features
13. Integrate AI features (summarization, suggestions)
14. Write and maintain documentation (README, API docs, architecture)
15. Set up CI/CD pipeline and deployment scripts
16. Plan for extensibility and future enhancements

## 2. Environment Isolation, Execution, and Configuration Strategy

- The application will use Python 3.12 for maximum stability and compatibility across the stack and packages.
- The project will be structured for maximum isolation:
  - All services (backend, frontend, database) will run in isolated containers managed by Docker Compose.
  - The Python backend will use a dedicated `.venv` and all dependencies will be managed via `requirements.txt` or `pyproject.toml`.
- A single, central app execution file (e.g., `run_app.sh` or `run_app.py`) will:
  - All setup, validation, and execution scripts must be written in Python to ensure cross-platform compatibility (no shell scripts).
  - Handle all setup, validation, and execution steps for the application through a single Python entrypoint (e.g., `run_app.py`).
  - Set up and export all environment variables and credentials from a single `.env` file provided by the user.
  - Dynamically generate and synchronize any required `.env` files for subcomponents, ensuring consistency.
  - Manage all architecture-related configuration in one place.
  - Provide debugging and diagnostic capabilities for all components (Docker, PostgreSQL, frontend, backend, design code, architecture, and package management).
  - Validate each step and component (Docker, backend, frontend, database) to ensure end-to-end connectivity and readiness before proceeding.
  - For PostgreSQL, perform initial setup (database, tables, fields), run health checks, and confirm operational status before application use.
  - Output all error and debug information to the terminal for transparency and troubleshooting.

## 3. Frontend, Backend, Reverse Proxy, and Docker Setup Strategy

- **Frontend**: Runs as a React app (Vite or Next.js) in a Docker container. Exposes port 3000 (default) and links to the backend API for data access.
- **Backend**: Runs as a FastAPI app in a Docker container. Exposes port 8000 (default) and connects to PostgreSQL for data storage.
- **PostgreSQL**: Runs in a Docker container. Exposes port 5432 (default) and is only accessible to backend and admin tools.
- **Nginx Reverse Proxy**: Runs in a Docker container as a reverse proxy for frontend and backend services. Exposes a single public port (e.g., 80 or 8080) and routes requests to the appropriate service:
  - `/api` and similar paths are forwarded to the backend
  - `/` and static assets are forwarded to the frontend
  - Hides internal service ports from external users
  - Provides a single entry point for all web traffic
- **Docker Compose**: Orchestrates all services (frontend, backend, database, nginx) with clear service definitions, build contexts, and environment variable injection from the main `.env` file.
- **Service Links**: Docker Compose networks ensure backend can reach database as `db:5432`, frontend can reach backend as `backend:8000`, and Nginx can reach both frontend and backend.
- **Colima**: Used for running Docker on macOS. For each run, both Docker Compose and Colima will be brought down and restarted to ensure a clean environment. The Python setup script will automate this process.
- **Service Health**: Each service will have health checks defined in `docker-compose.yml` to ensure readiness before dependent services start.
- **Scaling**: The architecture supports adding more services (e.g., AI, file storage) as needed, with clear port and network management.
- **Configuration**: All Docker and service configuration is centralized in `docker-compose.yml` and the main `.env` file, with no hardcoded values.

**Benefits of Nginx Reverse Proxy:**
- Centralizes routing and access control for all web traffic
- Improves security by hiding internal service ports
- Simplifies user access (single public port)
- Enables easy addition of HTTPS/SSL in the future
- Provides a foundation for advanced features (rate limiting, caching, etc.)

This strategy ensures a robust, reproducible, and cross-platform development and deployment environment, with clear separation of services, automated orchestration, and centralized configuration.
- Only one `.env` file will be user-facing; all other environment files will be generated as needed to maintain a single source of truth for configuration and credentials.

This approach ensures a robust, maintainable, and professional development workflow, with clear separation of concerns, maximum isolation, and centralized management of configuration and diagnostics.