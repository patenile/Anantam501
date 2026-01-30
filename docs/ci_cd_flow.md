# CI/CD Flow Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Anantam Home Interior Design Collaboration App. It covers each automation step, its setup, purpose, and how it works to ensure code quality, security, and reliable delivery.

---

## Overview
The CI/CD pipeline is powered by GitHub Actions and automates the following:
- Dependency installation and caching
- Linting and auto-formatting
- Unit, integration, and E2E testing
- Security scanning
- Code coverage reporting
- Docker image builds and tagging
- Automated deployment to Docker Hub
- Notifications (Slack)
- Dependency update automation (Dependabot)
- Scheduled security scans
- Code review automation (CODEOWNERS)
- Issue and PR templates for consistency

---

## Pipeline Steps and Purpose

### 1. Dependency Installation & Caching
- **Setup:** Uses pip for Python and npm for Node.js projects. Caches dependencies by Python/Node version and lockfiles.
- **Purpose:** Speeds up builds and ensures consistent environments.
- **How it works:** GitHub Actions cache actions restore dependencies if unchanged, otherwise install fresh.

### 2. Linting & Auto-formatting
- **Setup:** Runs flake8 (Python), eslint (JS/TS), black (Python), and prettier (JS/TS/MD).
- **Purpose:** Enforces code style and catches errors early.
- **How it works:** Fails the build if code is not properly formatted or contains lint errors.

### 3. Matrix Builds
- **Setup:** Tests against multiple Python (3.10, 3.11) and Node (18, 20) versions.
- **Purpose:** Ensures compatibility across environments.
- **How it works:** Runs jobs in parallel for each version combination.

### 4. Testing (Backend, Frontend, E2E)
- **Setup:**
  - Backend: pytest (with coverage)
  - Frontend: npm test (with coverage)
  - E2E: Playwright
- **Purpose:** Validates functionality, integration, and user flows.
- **How it works:** Runs tests, uploads results and coverage as artifacts.

### 5. Security Scanning
- **Setup:** pip-audit (Python), npm audit (Node), Trivy (Docker images).
- **Purpose:** Detects vulnerabilities in dependencies and images.
- **How it works:** Fails or warns on vulnerabilities; scheduled scan runs weekly.

### 6. Code Coverage Reporting
- **Setup:** pytest-cov (backend), Jest/Vitest (frontend). Artifacts uploaded; can be integrated with Codecov/Coveralls for live badges.
- **Purpose:** Tracks test coverage to prevent untested code.
- **How it works:** Generates and uploads coverage reports after tests.

### 7. Docker Image Build & Tagging
- **Setup:** Builds backend and frontend images, tags with latest, commit SHA, and branch.
- **Purpose:** Ensures traceable, reproducible deployments.
- **How it works:** Uses Docker Buildx and pushes images to Docker Hub.

### 8. Deployment
- **Setup:** Deploys images to Docker Hub using secrets for authentication.
- **Purpose:** Automates delivery to production or staging environments.
- **How it works:** Only runs on main branch; can be extended for staged environments.

### 9. Notifications
- **Setup:** Slack notifications for build success/failure.
- **Purpose:** Keeps the team informed of pipeline status.
- **How it works:** Uses Slack webhook secret; sends messages on workflow completion.

### 10. Dependency Update Automation
- **Setup:** Dependabot for pip and npm (weekly checks).
- **Purpose:** Keeps dependencies secure and up to date.
- **How it works:** Opens PRs for outdated/vulnerable dependencies.

### 11. Scheduled Security Scans
- **Setup:** Weekly scan job in workflow.
- **Purpose:** Regularly checks for new vulnerabilities.
- **How it works:** Runs all security scans on a schedule, not just on code changes.

### 12. Code Review Automation
- **Setup:** CODEOWNERS file assigns reviewers by path.
- **Purpose:** Ensures the right people review the right code.
- **How it works:** GitHub auto-requests reviews on PRs.

### 13. Issue and PR Templates
- **Setup:** Templates for bug reports, feature requests, and PRs.
- **Purpose:** Standardizes contributions and review process.
- **How it works:** Contributors are prompted to use templates when opening issues/PRs.

---

## How It Works (End-to-End)
1. Developer pushes code or opens a PR.
2. Workflow triggers: installs dependencies, restores cache, lints, formats, and tests code in all supported environments.
3. Security scans run on dependencies and Docker images.
4. Test and coverage results are uploaded as artifacts.
5. If on main branch, Docker images are built, tagged, and pushed to Docker Hub.
6. Slack notifications are sent on completion.
7. Dependabot runs weekly to update dependencies.
8. Scheduled security scan runs weekly.
9. CODEOWNERS and branch protection ensure code review and safe merges.

---

## Benefits
- Fast feedback and early error detection
- Consistent code style and quality
- Secure, up-to-date dependencies
- Automated, traceable deployments
- Team awareness via notifications
- Robust review and contribution process

---

For more details or to extend the pipeline, see `docs/future_recommendations.md` or ask for specific guidance.
