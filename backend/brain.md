# 🧠 Backend Brain — Meeting Task Manager API

A comprehensive reference for the backend codebase. Use this file to quickly understand the architecture, data models, API routes, services, and key design decisions.

---

## 📁 Project Structure

```
backend/
├── .env                        # Environment variables (DB, JWT, Azure OpenAI)
├── alembic.ini                 # Alembic config for DB migrations
├── requirements.txt            # Python dependencies
├── test.py / test_db.py        # Manual test scripts
│
├── alembic/
│   ├── env.py                  # Alembic environment setup
│   └── versions/
│       └── bb9f0cc3c251_initial_schema.py  # Initial DB migration
│
└── app/
    ├── main.py                 # FastAPI app entry point; registers all routers
    │
    ├── core/
    │   ├── config.py           # Settings loaded from .env via pydantic-settings
    │   └── security.py         # JWT creation/decoding, password hashing, get_current_user
    │
    ├── db/
    │   └── database.py         # SQLAlchemy engine, SessionLocal, Base, get_db()
    │
    ├── models/                 # SQLAlchemy ORM models (DB tables)
    │   ├── user.py             # User model
    │   ├── meeting.py          # Meeting model
    │   └── task.py             # Task model
    │
    ├── schemas/                # Pydantic models (request/response validation)
    │   ├── auth.py             # LoginRequest, TokenResponse, RefreshRequest
    │   ├── user.py             # UserCreate, UserResponse
    │   ├── meeting.py          # MeetingCreate, MeetingUpdate, MeetingResponse
    │   ├── meeting_ai.py       # MeetingUploadResponse (upload + AI task result)
    │   ├── task.py             # TaskCreate, TaskUpdate, TaskResponse
    │   ├── dashboard.py        # DashboardResponse
    │   └── ai.py               # AI-related schemas
    │
    ├── api/
    │   └── v1/                 # All API route handlers
    │       ├── auth.py         # /auth routes
    │       ├── user.py         # /users routes
    │       ├── meeting.py      # /meetings routes
    │       ├── task.py         # /tasks routes
    │       └── dashboard.py    # /dashboard routes
    │
    ├── services/               # Business logic layer
    │   ├── auth.py             # AuthService: register, login, refresh, get_current_user
    │   ├── user.py             # UserService: create, list, get by ID
    │   ├── meeting.py          # MeetingService: CRUD for meetings
    │   ├── task.py             # TaskService: CRUD + AI task creation
    │   ├── dashboard.py        # DashboardService: aggregate stats
    │   ├── ai.py               # AIService: calls Azure OpenAI to extract tasks
    │   └── transcript_extractor.py  # (stub/in progress)
    │
    ├── utils/
    │   └── transcript.py       # extract_text(): parse TXT, MD, PDF, DOCX files
    │
    └── prompts/
        └── extract_tasks.txt   # System prompt template for AI task extraction
```

---

## 🗄️ Database Models

### `User` — `users` table
| Column          | Type         | Notes                  |
|-----------------|--------------|------------------------|
| `id`            | Integer (PK) |                        |
| `full_name`     | String(100)  | Required               |
| `email`         | String(255)  | Unique, required       |
| `password_hash` | Text         | bcrypt hashed          |
| `created_at`    | TIMESTAMP    | Server default now()   |

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
| `status`       | String(20)   | `"pending"` or `"completed"`, default pending |
| `assignee_id`  | Integer (FK) | → `users.id` (who the task is for)           |
| `assigned_by`  | Integer (FK) | → `users.id` (who created the task)          |
| `meeting_id`   | Integer (FK) | → `meetings.id`, nullable                   |
| `created_at`   | TIMESTAMP    | Server default now()                         |
| `completed_at` | TIMESTAMP    | Nullable; set when task is completed         |

---

## 🔌 API Routes

### Auth — `/auth`
| Method | Path             | Auth Required | Description                                 |
|--------|------------------|:-------------:|---------------------------------------------|
| POST   | `/auth/login`    | ❌            | Login with email + password; returns tokens |
| POST   | `/auth/register` | ❌            | Register new user                           |
| POST   | `/auth/refresh`  | ❌            | Get new access token using refresh token    |
| GET    | `/auth/me`       | ✅            | Get currently authenticated user            |

### Users — `/users`
| Method | Path              | Auth Required | Description              |
|--------|-------------------|:-------------:|--------------------------|
| POST   | `/users/`         | ❌            | Create user (no auth)    |
| GET    | `/users/`         | ❌            | List all users           |
| GET    | `/users/{user_id}`| ❌            | Get user by ID           |

### Meetings — `/meetings`
| Method | Path                    | Auth Required | Description                                             |
|--------|-------------------------|:-------------:|---------------------------------------------------------|
| POST   | `/meetings/`            | ✅            | Create meeting manually (title + transcript body)       |
| POST   | `/meetings/upload`      | ✅            | Upload transcript file → save meeting → AI task extraction |
| GET    | `/meetings/`            | ✅            | List all meetings (ordered by newest first)             |
| GET    | `/meetings/{id}`        | ✅            | Get single meeting by ID                               |
| PUT    | `/meetings/{id}`        | ✅            | Update meeting (only by creator)                        |
| DELETE | `/meetings/{id}`        | ✅            | Delete meeting (only by creator)                        |

### Tasks — `/tasks`
| Method | Path                        | Auth Required | Description                                    |
|--------|-----------------------------|:-------------:|------------------------------------------------|
| POST   | `/tasks/`                   | ✅            | Create task manually                           |
| GET    | `/tasks/`                   | ✅            | List all tasks                                 |
| GET    | `/tasks/{task_id}`          | ✅            | Get task by ID                                 |
| PATCH  | `/tasks/{task_id}/complete` | ✅            | Mark task as completed (only assignee can do)  |
| GET    | `/tasks/user/{user_id}`     | ✅            | Get all tasks assigned to a specific user      |
| GET    | `/tasks/meeting/{meeting_id}`| ✅           | Get all tasks linked to a specific meeting     |
| PUT    | `/tasks/{task_id}`          | ✅            | Update task (assigner or assignee only)        |
| DELETE | `/tasks/{task_id}`          | ✅            | Delete task (assigner only)                    |

### Dashboard — `/dashboard`
| Method | Path          | Auth Required | Description                              |
|--------|---------------|:-------------:|------------------------------------------|
| GET    | `/dashboard/` | ✅            | Returns aggregate stats for the platform |

**Dashboard Response fields:**
- `total_meetings` — Total number of meetings
- `total_tasks` — Total number of tasks
- `pending_tasks` — Tasks with status `"pending"`
- `completed_tasks` — Tasks with status `"completed"`
- `completion_rate` — `(completed / total) * 100`, rounded to 2 decimal places

---

## ⚙️ Core Modules

### `app/core/config.py` — Settings
Loads all environment variables via `pydantic-settings`:

```python
settings.DATABASE_URL
settings.SECRET_KEY
settings.ALGORITHM                   # default: HS256
settings.ACCESS_TOKEN_EXPIRE_MINUTES # default: 15 min (env sets 30)
settings.REFRESH_TOKEN_EXPIRE_DAYS   # default: 30 days (env sets 7)
settings.AZURE_OPENAI_API_KEY
settings.AZURE_OPENAI_ENDPOINT
settings.AZURE_OPENAI_API_VERSION
settings.AZURE_OPENAI_DEPLOYMENT
```

### `app/core/security.py` — Auth & JWT
| Function              | Description                                                              |
|-----------------------|--------------------------------------------------------------------------|
| `hash_password()`     | Hashes a plain password with bcrypt                                      |
| `verify_password()`   | Verifies plain vs hashed password                                        |
| `create_access_token()` | Creates a JWT with `type: "access"` and expiry                        |
| `create_refresh_token()` | Creates a JWT with `type: "refresh"` and expiry                      |
| `decode_access_token()` | Decodes and validates access token type                                |
| `decode_refresh_token()` | Decodes and validates refresh token type                              |
| `get_current_user()`  | FastAPI dependency — extracts user from Bearer token, returns `User` obj |

OAuth2 token URL: `/auth/login`

### `app/db/database.py` — Database
- Creates a SQLAlchemy engine from `settings.DATABASE_URL`
- `SessionLocal` — session factory
- `Base` — declarative base for all models
- `get_db()` — FastAPI dependency that yields a session and closes it after

---

## 🤖 AI Integration

### `app/services/ai.py` — AIService
- Client: `AzureOpenAI` with credentials from `settings`
- Deployment: `gpt4-interview` (configurable via env)
- Temperature: `0.2` (low, for deterministic task extraction)
- Response format: `json_object`

**System Prompt behavior:**
- Reads the transcript
- Returns ONLY a JSON object: `{ "tasks": [ { "title", "description", "assignee" } ] }`
- Returns `{ "tasks": [] }` if no tasks found
- Uses `null` for assignee if not mentioned

**`AIService.generate_tasks(transcript: str) → list[dict]`**
- Calls Azure OpenAI
- Parses JSON response
- Returns list of task dicts; empty list on failure

### `app/services/task.py` — `create_ai_tasks()`
After AI generates tasks, this method:
1. Validates the meeting exists
2. For each AI task:
   - Skips if `title` is missing
   - Skips if no `assignee` name returned
   - Does a **case-insensitive** `ilike` lookup on `User.name` (⚠️ note: model uses `full_name`, not `name` — potential bug)
   - Skips if user not found in DB
3. Bulk-commits all created tasks
4. Returns `{ "created": [...], "skipped": [...] }` with skip reasons

---

## 📤 File Upload & Transcript Extraction

### `app/utils/transcript.py` — `extract_text(file: UploadFile) → str`
Supports these file types:

| Extension | Library   |
|-----------|-----------|
| `.txt`    | Built-in  |
| `.md`     | Built-in  |
| `.pdf`    | PyPDF2    |
| `.docx`   | python-docx |

Raises HTTP 400 for unsupported file types.

---

## 🔐 Authorization Rules

| Action                | Who Can Do It                        |
|-----------------------|--------------------------------------|
| Update a meeting      | Only the user who uploaded it        |
| Delete a meeting      | Only the user who uploaded it        |
| Complete a task       | Only the assignee                    |
| Update a task         | Assignee or assigner                 |
| Delete a task         | Only the assigner                    |

---

## 🧩 Key Design Patterns

- **Service Layer**: All business logic lives in `app/services/`. Routers are thin and just delegate to services.
- **Static Methods**: Services use `@staticmethod` — no class instantiation needed.
- **Pydantic Schemas**: Separate schemas for `Create`, `Update`, and `Response` per resource.
- **Dependency Injection**: `get_db()` and `get_current_user()` are FastAPI `Depends()` dependencies used across all protected routes.
- **Alembic Migrations**: DB schema managed via Alembic. Initial migration in `versions/bb9f0cc3c251_initial_schema.py`.

---

## ⚠️ Known Issues / TODOs

| Issue | Location | Details |
|-------|----------|---------|
| Wrong column name in AI task user lookup | `services/task.py` L320 | Uses `User.name.ilike(...)` but the model column is `full_name` — will cause a runtime AttributeError |
| `transcript_extractor.py` is empty/stub | `services/transcript_extractor.py` | Likely intended for a future audio transcription feature |
| `/users/` endpoints have no auth | `api/v1/user.py` | Any unauthenticated user can list all users or create users directly |
| `get_meetings()` ignores `current_user` | `services/meeting.py` | Returns all meetings from all users; no per-user filtering |
| `get_tasks()` ignores `current_user` | `services/task.py` | Returns all tasks; no per-user filtering |
| Dashboard ignores `current_user` | `services/dashboard.py` | Returns global stats, not per-user stats |
| `auth.py` schemas duplicate `user.py` schemas | `schemas/auth.py` | Defines `UserCreate` and `UserResponse` again — can cause import confusion |

---

## 🚀 Running the Backend

```bash
# From the /backend directory
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## 📦 Dependencies

| Package               | Purpose                              |
|-----------------------|--------------------------------------|
| `fastapi`             | Web framework                        |
| `uvicorn[standard]`   | ASGI server                          |
| `sqlalchemy`          | ORM                                  |
| `psycopg2-binary`     | PostgreSQL driver                    |
| `pydantic`            | Data validation                      |
| `pydantic-settings`   | Settings from `.env`                 |
| `python-dotenv`       | Load `.env` file                     |
| `python-multipart`    | File upload support (`UploadFile`)   |
| `passlib[bcrypt]`     | Password hashing                     |
| `python-jose[cryptography]` | JWT creation/decoding          |
| `alembic`             | DB migrations                        |
| `email-validator`     | Validates `EmailStr` in Pydantic     |
| `openai`              | Azure OpenAI client (implied by import) |
| `PyPDF2`              | PDF text extraction                  |
| `python-docx`         | DOCX text extraction                 |
