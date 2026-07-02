# 🧠 Backend Brain — Meeting Task Manager API

A comprehensive reference for the backend codebase. Use this file to quickly understand the architecture, data models, API routes, services, and key design decisions.

---

## 📁 Project Structure

```
backend/
├── .env.example                # Example environment variables
├── alembic.ini                 # Alembic config for DB migrations
├── requirements.txt            # Dev dependencies (FastAPI, pytest)
├── requirements.prod.txt       # Prod dependencies (Gunicorn)
├── Dockerfile                  # Production two-stage Docker image
├── entrypoint.sh               # Startup script (runs migrations then Gunicorn)
│
├── alembic/
│   ├── env.py                  # Alembic environment setup
│   └── versions/
│       ├── bb9f0cc3c251_initial_schema.py
│       ├── ce8a5d5dfc0b_add_team_code_to_users.py
│       └── 356f56584964_add_refresh_tokens_table.py
│
├── app/
│   ├── main.py                 # FastAPI app entry point; registers routers + CORS
│   │
│   ├── core/
│   │   ├── config.py           # Settings loaded via pydantic-settings
│   │   ├── security.py         # JWT creation/decoding, get_current_user
│   │   └── pagination.py       # Pagination dependencies (skip/limit)
│   │
│   ├── db/
│   │   └── database.py         # SQLAlchemy engine, SessionLocal, get_db()
│   │
│   ├── models/                 # SQLAlchemy ORM models (DB tables)
│   │   ├── user.py             # User model
│   │   ├── meeting.py          # Meeting model
│   │   ├── task.py             # Task model
│   │   ├── notification.py     # Notification model
│   │   └── refresh_token.py    # RefreshToken model
│   │
│   ├── schemas/                # Pydantic models (request/response validation)
│   │   ├── auth.py             
│   │   ├── user.py             
│   │   ├── meeting.py          
│   │   ├── meeting_ai.py       
│   │   ├── task.py             
│   │   ├── dashboard.py        
│   │   ├── notification.py
│   │   └── ai.py               
│   │
│   ├── api/
│   │   └── v1/                 # All API route handlers
│   │       ├── auth.py         
│   │       ├── user.py         
│   │       ├── meeting.py      
│   │       ├── task.py         
│   │       ├── dashboard.py    
│   │       └── notification.py 
│   │
│   ├── services/               # Business logic layer
│   │   ├── auth.py             # Login, register, refresh, logout (token rotation)
│   │   ├── user.py             # User CRUD (team-scoped)
│   │   ├── meeting.py          # Meeting CRUD (team-scoped)
│   │   ├── task.py             # Task CRUD (team-scoped) + AI processing
│   │   ├── dashboard.py        # Stats (team-scoped)
│   │   ├── notification.py     # Notification CRUD
│   │   └── ai.py               # Calls Azure OpenAI
│   │   
│   └── utils/
│       └── transcript.py       # Extract text from TXT/MD/PDF/DOCX + size limits
│
└── tests/
    ├── conftest.py             # Test DB setup and fixtures
    ├── test_auth.py            # Auth + refresh token tests
    ├── test_tasks.py           # Task CRUD + team scope tests
    └── test_ai_tasks.py        # AI task extraction tests
```

---

## 🗄️ Database Models

### `User` — `users` table
| Column          | Type         | Notes                  |
|-----------------|--------------|------------------------|
| `id`            | Integer (PK) |                        |
| `full_name`     | String(100)  | Required               |
| `email`         | String(255)  | Required               |
| `password_hash` | Text         | bcrypt hashed          |
| `team_code`     | String(50)   | Used for multi-tenant isolation |
| `created_at`    | TIMESTAMP    | Server default now()   |

*Note: `(email, team_code)` is a UniqueConstraint.*

### `RefreshToken` — `refresh_tokens` table
| Column         | Type         | Notes                        |
|----------------|--------------|------------------------------|
| `id`           | Integer (PK) |                              |
| `token_hash`   | String(64)   | SHA-256 hash of the JWT      |
| `user_id`      | Integer (FK) | → `users.id` (cascade delete)|
| `is_revoked`   | Boolean      | Default `False`              |
| `expires_at`   | TIMESTAMP    | Must match JWT `exp` claim   |

### `Meeting` — `meetings` table
| Column        | Type         | Notes                        |
|---------------|--------------|------------------------------|
| `id`          | Integer (PK) |                              |
| `title`       | String(255)  |                              |
| `transcript`  | Text         | Full meeting transcript      |
| `uploaded_by` | Integer (FK) | → `users.id`                 |
| `created_at`  | TIMESTAMP    | Server default now()         |

### `Task` — `tasks` table
| Column         | Type         | Notes                                        |
|----------------|--------------|----------------------------------------------|
| `id`           | Integer (PK) |                                              |
| `title`        | String(255)  | Required                                     |
| `description`  | Text         | Optional                                     |
| `status`       | String(20)   | `"pending"` or `"completed"`                 |
| `priority`     | String(20)   | `"low"`, `"medium"`, `"high"`, `"critical"`  |
| `assignee_id`  | Integer (FK) | → `users.id`                                 |
| `assigned_by`  | Integer (FK) | → `users.id`                                 |
| `meeting_id`   | Integer (FK) | → `meetings.id`, nullable                    |
| `due_date`     | Date         | Optional                                     |
| `created_at`   | TIMESTAMP    | Server default now()                         |
| `completed_at` | TIMESTAMP    | Nullable                                     |

### `Notification` — `notifications` table
| Column         | Type         | Notes                                        |
|----------------|--------------|----------------------------------------------|
| `id`           | Integer (PK) |                                              |
| `user_id`      | Integer (FK) | → `users.id`                                 |
| `title`        | String(255)  |                                              |
| `message`      | Text         |                                              |
| `type`         | String(50)   | e.g. `"task_assigned"`, `"task_reassigned"`  |
| `task_id`      | Integer (FK) | → `tasks.id`, nullable                       |
| `is_read`      | Boolean      | Default `False`                              |

---

## 🔌 API Routes

See `docs/API.md` for a full endpoint reference with request/response examples.

---

## 🛡️ Security & Multi-tenancy (Team Code)

### Team Isolation
Every user belongs to a `team_code`. All lookups in the application are scoped to the `current_user.team_code`. 
- `MeetingService` filters by team members' meetings.
- `TaskService` blocks creating a task for a user outside your team.
- `UserService` only returns users in your team.

### Token Rotation
- Login issues an `access_token` (30m) and `refresh_token` (7d).
- Refresh tokens are hashed via SHA-256 and stored in the `refresh_tokens` table.
- A `jti` (UUID) claim is embedded in tokens to prevent hash collisions.
- Calling `/auth/refresh` immediately **revokes** the old refresh token and issues a new pair (Refresh Token Rotation).
- Calling `/auth/logout` explicitly revokes a token.

---

## ⚙️ Core Modules

### `app/core/config.py` — Settings
Loads environment variables. Key configs:
- `MAX_TRANSCRIPT_CHARS`: Prevents giant file uploads blowing through OpenAI token limits.
- `ALLOWED_ORIGINS`: Used by CORS middleware to lock down domains in production.

### `app/db/database.py` — Database
- Yields SQLAlchemy `Session` via `get_db()`.
- **Note:** `Base.metadata.create_all()` is NOT used on startup. Alembic exclusively manages the schema.

---

## 🤖 AI Integration

### `app/services/ai.py`
Calls Azure OpenAI GPT-4 with a low temperature (`0.2`) and strict `json_object` format to extract tasks from a transcript.

### `app/services/task.py` -> `create_ai_tasks()`
- AI returns an assignee string.
- System attempts a case-insensitive match against `full_name` of users in the current team.
- If no match (or missing assignee), the task is **auto-assigned** to the team member with the fewest pending tasks (`_get_least_loaded_user()`).

---

## 🧪 Testing

The backend includes a comprehensive pytest suite (`tests/`).

### Test DB Architecture
- `conftest.py` uses SQLAlchemy transactions to wrap each test.
- Every test rolls back at the end.
- This ensures test isolation without needing to recreate/drop tables for every test case.

Run tests via:
```bash
python -m pytest tests/ -v
```

---

## 🚀 Docker & Deployment

The backend is fully containerised for production (Azure Container Apps).

- **Dockerfile**: Two-stage build. Uses `python:3.11-slim`. Stage 1 compiles requirements in a venv; Stage 2 runs the app as a non-root user.
- **entrypoint.sh**: Automatically runs `alembic upgrade head` before starting `gunicorn` with Uvicorn workers.

---

## 🧩 Key Design Patterns

- **Service Layer**: Business logic lives in `app/services/`. API routers just validate I/O and call services.
- **Dependency Injection**: `get_db()` and `get_current_user()` handle cross-cutting concerns (DB sessions and Auth) securely.
- **Cascading Deletes**: Handled at the database level (`ondelete="CASCADE"`), though most data is retained for history.
