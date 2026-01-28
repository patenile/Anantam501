# Home Interior Design Collaboration App: Requirements & Architecture

## Integration & Embedding Guidelines

To ensure this application can be easily integrated into existing or future systems (e.g., as a Dashboard card or micro-frontend), follow these principles:

- **Modular Frontend**: Build the UI as a self-contained React (or web component) module that can be embedded as a card or widget in other dashboards.
- **API-First Backend**: Expose all features via RESTful (or GraphQL) APIs, so any external dashboard can interact with the app’s data and logic.
- **Authentication**: Use token-based authentication (JWT/OAuth) to allow secure cross-app integration.
- **Decoupled Design**: Avoid hard dependencies on specific frontend or backend frameworks; keep interfaces clean and well-documented.
- **Microservice-Ready**: Structure backend so it can run as a standalone service or be called from other services.
- **Shared Styles/Design System**: If your existing dashboard uses a design system, plan to align or theme this app for visual consistency.
- **Documentation**: Clearly document integration points and embed options.

This approach will let you add the app as a dashboard card, iframe, or micro-frontend, or even merge its backend into a larger system later.

## 1. High-Level Data Model & System Architecture

### Directory & Infra Organization
- All infrastructure and deployment files are under `infra/`:
  - `infra/docker-compose.yml` (service orchestration)
  - `infra/nginx/` (proxy configs, etc.)
- Application code is in `backend/` and `frontend/`.
- Root contains only project-level config and documentation.

### Entities
- **Users** (Admin, Manager, Team, Family)
- **Home**
- **Room** (belongs to Home)
- **RoomElement** (belongs to Room)
- **Comment** (belongs to Room or RoomElement)
- **Assignment** (links Team Members to Rooms/Elements)
- **PurchaseDetail** (belongs to RoomElement)
- **ImportFile** (for floor plan/layout import)

### System Architecture
- **Frontend**: React or template-based UI
- **Backend API**: FastAPI or Django
- **Database**: PostgreSQL (local or Docker)
- **AI Service**: OpenAI API or similar for summarization/suggestions
- **File Storage**: Local/cloud for images, imports, attachments

---

## 2. Text-Based ER Diagram

```
User
 ├─ id (PK)
 ├─ name
 ├─ email
 ├─ role (admin, manager, team, family)
 └─ ...

Home
 ├─ id (PK)
 ├─ name
 ├─ address
 └─ owner_id (FK: User)

Room
 ├─ id (PK)
 ├─ home_id (FK: Home)
 ├─ name
 ├─ description
 ├─ measurements
 └─ ...

RoomElement
 ├─ id (PK)
 ├─ room_id (FK: Room)
 ├─ name
 ├─ description
 ├─ measurements
 └─ ...

Comment
 ├─ id (PK)
 ├─ user_id (FK: User)
 ├─ room_id (FK: Room, nullable)
 ├─ element_id (FK: RoomElement, nullable)
 ├─ content
 ├─ ai_summary (optional, for AI summarization)
 ├─ created_at
 └─ ...

Assignment
 ├─ id (PK)
 ├─ user_id (FK: User)
 ├─ room_id (FK: Room, nullable)
 ├─ element_id (FK: RoomElement, nullable)
 ├─ assigned_by (FK: User)
 └─ ...

PurchaseDetail
 ├─ id (PK)
 ├─ element_id (FK: RoomElement)
 ├─ status
 ├─ vendor
 ├─ cost
 ├─ link
 └─ ...

ImportFile
 ├─ id (PK)
 ├─ user_id (FK: User)
 ├─ file_path
 ├─ import_type
 └─ ...
```

---

## 3. API Outline & Module Breakdown

### Auth Module
- POST /auth/login
- POST /auth/register (admin only)
- POST /auth/invite (admin/manager)
- POST /auth/logout

### User/Team Module
- GET /users/
- POST /users/ (admin/manager)
- PATCH /users/{id}
- DELETE /users/{id}

### Home/Room Module
- GET /homes/
- POST /homes/
- PATCH /homes/{id}
- DELETE /homes/{id}
- GET /rooms/?home_id=
- POST /rooms/
- PATCH /rooms/{id}
- DELETE /rooms/{id}

### Room Element Module
- GET /elements/?room_id=
- POST /elements/
- PATCH /elements/{id}
- DELETE /elements/{id}

### Comment Module
- GET /comments/?room_id=&element_id=
- POST /comments/
- DELETE /comments/{id}

### Assignment Module
- POST /assignments/
- PATCH /assignments/{id}
- DELETE /assignments/{id}

### Purchase Module
- GET /purchases/?element_id=
- POST /purchases/
- PATCH /purchases/{id}
- DELETE /purchases/{id}

### Import/Export Module
- POST /import/
- GET /export/

### AI Module
- POST /ai/summarize (comments)
- POST /ai/suggest (design ideas)

---

## Detailed Data Models

### User
- id: UUID (PK)
- name: string
- email: string (unique, indexed)
- password_hash: string
- role: enum (admin, manager, team, family)
- is_active: boolean (default: true)
- created_at: datetime
- updated_at: datetime

### Home
- id: UUID (PK)
- name: string
- address: string
- owner_id: UUID (FK: User)
- created_at: datetime
- updated_at: datetime

### Room
- id: UUID (PK)
- home_id: UUID (FK: Home, indexed)
- name: string
- description: text
- measurements: jsonb (length, width, height, area, etc.)
- created_at: datetime
- updated_at: datetime

### RoomElement
- id: UUID (PK)
- room_id: UUID (FK: Room, indexed)
- name: string
- description: text
- measurements: jsonb (length, width, height, etc.)
- created_at: datetime
- updated_at: datetime

### Comment
- id: UUID (PK)
- user_id: UUID (FK: User, indexed)
- room_id: UUID (FK: Room, nullable, indexed)
- element_id: UUID (FK: RoomElement, nullable, indexed)
- content: text
- ai_summary: text (optional, for AI summarization)
- created_at: datetime
- updated_at: datetime

### Assignment
- id: UUID (PK)
- user_id: UUID (FK: User, indexed)
- room_id: UUID (FK: Room, nullable, indexed)
- element_id: UUID (FK: RoomElement, nullable, indexed)
- assigned_by: UUID (FK: User)
- assigned_at: datetime
- status: enum (pending, in_progress, completed)

### PurchaseDetail
- id: UUID (PK)
- element_id: UUID (FK: RoomElement, indexed)
- status: enum (planned, ordered, delivered, installed)
- vendor: string
- cost: decimal
- link: string (URL)
- notes: text
- created_at: datetime
- updated_at: datetime

### ImportFile
- id: UUID (PK)
- user_id: UUID (FK: User)
- file_path: string
- import_type: enum (image, pdf, csv, json)
- imported_at: datetime
- status: enum (pending, processed, failed)
- notes: text

---

## URL Validation & Security

- All URLs submitted by users must be validated in the backend before being proxied, stored, or used in the application.
- Validation includes:
  - Only allow URLs from a configurable allowlist of domains (see nginx config).
  - Require HTTPS scheme.
  - Perform a safe HEAD/GET request with a timeout and content-type check.
  - Enforce a maximum content size (e.g., 10MB).
  - Reject URLs with dangerous redirects or suspicious content types.
  - Log and reject any suspicious or unsafe URLs.
- The backend must sanitize and escape all URLs before storing or displaying them.
- All proxying must go through the nginx url-proxy service for additional security and caching.

---

## Finalization & Locking Policy

- Any entity (Room, RoomElement, PurchaseDetail, etc.) can be marked as "finalized" (locked).
- When finalized, only the Interior Manager or Admin can make further changes; all other users have read-only access to that entity.
- Add a `finalized` boolean field and `finalized_at` datetime field to relevant models (Room, RoomElement, PurchaseDetail).
- UI should clearly indicate when an item is finalized/locked.
- All update/delete API endpoints must enforce this policy at the backend.
- Audit log should record who finalized/unlocked an entity and when.

This ensures important decisions are protected and only authorized users can override them if necessary.

---

- All UUIDs are generated by the backend.
- All datetime fields are timezone-aware.
- Indexes on foreign keys and frequently queried fields for performance.
- Use enums for roles and statuses for data integrity.
- Use jsonb for flexible measurement storage.

Let me know if you want to review or adjust any model before we move to the architecture diagram and project scaffolding.
