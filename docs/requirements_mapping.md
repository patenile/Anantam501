# Requirements to Implementation Mapping

## 1. User Authentication & Authorization
- **Implemented in:**
  - backend/main.py (endpoints: /auth/register, /auth/login)
  - backend/models.py (User model)
  - backend/schemas.py (UserCreate, UserLogin, UserOut)
  - backend/database.py (DB connection)
  - backend/tests/test_auth.py (tests)
- **Pending:**
  - Password reset/change, OAuth2, advanced permissions

## 2. User Profile Management
- **Implemented in:**
  - backend/models.py (User fields)
  - backend/schemas.py (UserOut)
- **Pending:**
  - Avatar upload, profile update endpoint

## 3. Health Check & Status
- **Implemented in:**
  - backend/main.py (likely /health or / endpoint)

## 4. Audit Logging & Activity Tracking
- **Pending:**
  - Not implemented

## 5. Error Handling & Standardized Responses
- **Implemented in:**
  - FastAPI default, backend/main.py

## 6. Pagination, Filtering, Sorting
- **Pending:**
  - Not implemented in list endpoints

## 7. File Upload/Download
- **Pending:**
  - Not implemented

## 8. API Documentation
- **Implemented in:**
  - FastAPI auto-generated docs (backend/main.py)

## 9. Admin/Management Endpoints
- **Implemented in:**
  - backend/main.py (user/project endpoints, role fields)
- **Pending:**
  - System settings, advanced admin features

## 10. Notifications
- **Pending:**
  - Not implemented

## Entities & Data Models
- **Implemented:**
  - User, Project (backend/models.py, backend/schemas.py)
- **Pending:**
  - Home, Room, RoomElement, Comment, Assignment, PurchaseDetail, ImportFile

## API Endpoints
- **Implemented:**
  - /auth/*, /users/*, /projects/* (backend/main.py)
- **Pending:**
  - All endpoints for Home, Room, RoomElement, Comment, Assignment, Purchase, Import/Export, AI

## AI/MCP Assistant
- **Pending:**
  - Not implemented

## Finalization/Locking Policy
- **Pending:**
  - Not implemented

## URL Validation & Security
- **Pending:**
  - Not implemented

## File Storage
- **Pending:**
  - Not implemented

## Testing & CI
- **Implemented in:**
  - scripts/test_with_services.py (orchestration)
  - backend/tests/ (test files)
  - .github/workflows/ci-cd.yml (CI)

---

# Suggested Tickets (Todos)

1. Implement Home, Room, RoomElement, Comment, Assignment, PurchaseDetail, ImportFile models and endpoints
2. Add pagination, filtering, and sorting to list endpoints
3. Implement file upload/download and import/export endpoints
4. Add audit logging and activity tracking
5. Integrate notifications (email/in-app)
6. Add finalization/locking logic to relevant models and endpoints
7. Implement URL validation and proxying
8. Integrate MCP assistant and AI endpoints
9. Build user-facing template UI
10. Harden and document platform for reuse
11. Automate full app creation from template document
12. Set up CI/CD for template-driven workflow
