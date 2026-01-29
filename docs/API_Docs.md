# API Documentation and Test Plan

## API Endpoints

### 1. `GET /`
- **Purpose:** Health check for backend service.
- **Description:** Returns a simple message to confirm the backend is running.

### 2. `POST /auth/register`
- **Purpose:** Register a new user.
- **Description:** Accepts email, password, and full name. Creates a new user if the email is unique and the password meets requirements.

### 3. `POST /auth/login`
- **Purpose:** Authenticate a user and issue a JWT token.
- **Description:** Accepts email and password. Returns an access token if credentials are valid.

### 4. `GET /users/me`
- **Purpose:** Get the current authenticated user's info.
- **Description:** Requires a valid JWT token. Returns user details for the authenticated user.

---

## Test Plan for Each API

### 1. `GET /` (Health Check)
- **Test Purpose:** Ensure backend is up and responding.
- **How:** Send GET request, expect 200 and correct message.
- **Why Needed:** Detects if backend is running in CI/CD and for uptime monitoring.

### 2. `POST /auth/register`
- **Test Purpose:** Ensure user registration works and enforces all rules.
- **How:**
  - Register with valid data (expect 200, user created)
  - Register with invalid email (expect 422)
  - Register with short password (expect 422)
  - Register with duplicate email (expect 400)
- **Why Needed:** Prevents invalid or insecure user creation, enforces business rules, and ensures error handling.

### 3. `POST /auth/login`
- **Test Purpose:** Ensure login only works with correct credentials.
- **How:**
  - Login with correct credentials (expect 200, token returned)
  - Login with wrong password (expect 401)
  - Login with non-existent user (expect 401)
- **Why Needed:** Prevents unauthorized access and ensures authentication is secure.

### 4. `GET /users/me`
- **Test Purpose:** Ensure only authenticated users can access their info.
- **How:**
  - Access with valid token (expect 200, user info)
  - Access with no token (expect 401)
  - Access with invalid/expired token (expect 401)
- **Why Needed:** Protects user data and enforces authentication for sensitive endpoints.

---

## How Tests Are Implemented
- **Framework:** pytest + requests
- **Approach:**
  - Each endpoint is tested for both success and failure cases.
  - Edge cases (invalid input, duplicate, unauthorized) are explicitly tested.
  - Tests run in CI/CD to catch regressions and security issues early.

---

*Expand this document as new endpoints are added.*
