# Meeting Task Manager

> **AI-powered meeting task management platform.** Upload a meeting transcript, let GPT-4 extract action items automatically, assign them to team members, and track progress — all in one place.

![Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Stack](https://img.shields.io/badge/Frontend-Next.js_16-000000?style=flat-square&logo=nextdotjs)
![Stack](https://img.shields.io/badge/Database-PostgreSQL_16-4169E1?style=flat-square&logo=postgresql)
![Stack](https://img.shields.io/badge/AI-Azure_OpenAI-0078D4?style=flat-square&logo=microsoftazure)
![Stack](https://img.shields.io/badge/Deploy-Azure_Container_Apps-0078D4?style=flat-square&logo=microsoftazure)

---

## Features

| Feature | Detail |
|---|---|
| 📋 **Meeting management** | Create meetings manually or upload a transcript file (TXT, MD, PDF, DOCX) |
| 🤖 **AI task extraction** | GPT-4 reads the transcript and extracts actionable tasks with assignees, priorities, and due dates |
| 👥 **Multi-team support** | Each team gets a unique Team Code; users are fully isolated between teams |
| ✅ **Task tracking** | Assign, update, complete, and delete tasks with granular permissions |
| 🔔 **Notifications** | In-app notifications for task assignments and reassignments |
| 📊 **Dashboard** | Per-user stats — tasks assigned to you, tasks you created, completion rates |
| 🔒 **Secure auth** | JWT access + refresh tokens, token rotation on every refresh, server-side revocation |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Azure Container Apps               │
│                                                     │
│   ┌──────────────┐        ┌─────────────────────┐  │
│   │  Next.js 16  │ ──────▶│    FastAPI (Python)  │  │
│   │  (frontend)  │  HTTP  │    + Gunicorn        │  │
│   └──────────────┘        └──────────┬──────────┘  │
│                                      │              │
│                           ┌──────────▼──────────┐  │
│                           │  PostgreSQL 16       │  │
│                           │  (Azure Flexible)    │  │
│                           └─────────────────────┘  │
│                                                     │
│   External: Azure OpenAI (GPT-4)                   │
└─────────────────────────────────────────────────────┘
```

### Backend structure

```
backend/
├── app/
│   ├── api/v1/          # Route handlers (thin — delegate to services)
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── meeting.py
│   │   ├── task.py
│   │   ├── dashboard.py
│   │   └── notification.py
│   ├── core/            # Config, security, logging, pagination
│   ├── db/              # SQLAlchemy engine + session
│   ├── models/          # ORM models (User, Meeting, Task, Notification, RefreshToken)
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic (auth, meeting, task, ai, notification, dashboard)
│   └── utils/           # Transcript text extraction
├── alembic/             # Database migrations
├── tests/               # 33 pytest tests
├── Dockerfile           # Two-stage production image
├── entrypoint.sh        # Migrations → Gunicorn startup
└── requirements.prod.txt
```

---

## Quick Start (local development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16
- An [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) resource with a GPT-4 deployment

### 1. Clone and set up environment

```bash
git clone <repo-url>
cd meeting-task-manager
```

### 2. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and fill in your environment variables
cp .env.example .env
# Edit .env with your database URL, secret key, Azure OpenAI credentials

# Run migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy and fill in environment
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start the development server
npm run dev
```

Frontend is available at `http://localhost:3000`

### 4. Run tests

```bash
cd backend
pytest tests/ -v
```

---

## Docker (local full-stack)

```bash
# From project root — starts backend + frontend + local Postgres
docker compose up --build
```

Visit `http://localhost:3000`

---

## Environment Variables

### Backend (`.env`)

| Variable | Required | Example | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql://user:pass@localhost:5432/db` | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | `<random 32-byte string>` | JWT signing secret |
| `ALGORITHM` | ✅ | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ✅ | `7` | Refresh token lifetime |
| `AZURE_OPENAI_API_KEY` | ✅ | `abc123...` | Azure OpenAI key |
| `AZURE_OPENAI_ENDPOINT` | ✅ | `https://name.openai.azure.com/` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_VERSION` | ✅ | `2024-12-01-preview` | API version |
| `AZURE_OPENAI_DEPLOYMENT` | ✅ | `gpt4-interview` | Deployment name |
| `ALLOWED_ORIGINS` | optional | `https://app.yourdomain.com` | Comma-separated CORS origins (dev fallback: localhost) |
| `MAX_TRANSCRIPT_CHARS` | optional | `50000` | Max transcript size sent to AI |
| `WORKERS` | optional | `2` | Gunicorn worker count (production) |
| `LOG_LEVEL` | optional | `info` | Logging verbosity |

### Frontend (`.env.local`)

| Variable | Required | Example | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | `http://localhost:8000` | Backend API base URL |

---

## Team Code System

The platform supports multiple isolated teams. Each team is identified by a **Team Code** (e.g. `ACME-2024`).

- Users register with an email **and** a Team Code
- The same email can belong to multiple teams (separate accounts)
- All data (meetings, tasks, users) is fully scoped to a team — cross-team access returns `404`
- Share your Team Code with colleagues so they can join your team

---

## Authentication Flow

```
Register ──────────────────────────────────────────────────▶ User created
                                                              (email + team_code unique)

Login ─────────────────────────────────────────────────────▶ access_token (30 min)
                                                           ▶ refresh_token (7 days, stored hashed in DB)

API Request ───(Authorization: Bearer <access_token>)──────▶ Protected endpoint

Token Refresh ─(POST /auth/refresh with refresh_token)─────▶ new access_token
                                                           ▶ new refresh_token (old one revoked)

Logout ────────(POST /auth/logout with refresh_token)──────▶ refresh_token revoked in DB
```

---

## AI Task Extraction

When a transcript is uploaded:

1. Text is extracted from the file (TXT / MD / PDF / DOCX)
2. The transcript is validated (max 10 MB file, 50,000 characters)
3. Azure OpenAI GPT-4 reads the transcript and returns structured JSON with tasks
4. Each task includes: `title`, `description`, `assignee`, `priority`, `due_date`
5. Assignees are matched to team members by name (case-insensitive)
6. Unmatched assignees are **auto-assigned** to the team member with the fewest pending tasks
7. All created tasks trigger in-app notifications to assignees

---

## API Reference

Full interactive API documentation is available at `http://localhost:8000/docs` when running locally.

### Endpoints summary

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register a new user |
| `POST` | `/auth/login` | ❌ | Login and receive tokens |
| `POST` | `/auth/refresh` | ❌ | Rotate refresh token |
| `POST` | `/auth/logout` | ✅ | Revoke refresh token |
| `GET` | `/auth/me` | ✅ | Get current user |
| `GET` | `/users/` | ✅ | List team members |
| `GET` | `/users/{id}` | ✅ | Get user by ID |
| `POST` | `/meetings/` | ✅ | Create meeting manually |
| `POST` | `/meetings/upload` | ✅ | Upload transcript + AI extract tasks |
| `GET` | `/meetings/` | ✅ | List your meetings |
| `GET` | `/meetings/{id}` | ✅ | Get meeting (team-scoped) |
| `PUT` | `/meetings/{id}` | ✅ | Update meeting |
| `DELETE` | `/meetings/{id}` | ✅ | Delete meeting |
| `POST` | `/tasks/` | ✅ | Create task |
| `GET` | `/tasks/` | ✅ | List your tasks |
| `GET` | `/tasks/{id}` | ✅ | Get task (team-scoped) |
| `PUT` | `/tasks/{id}` | ✅ | Update task |
| `PATCH` | `/tasks/{id}/complete` | ✅ | Mark task complete |
| `DELETE` | `/tasks/{id}` | ✅ | Delete task |
| `GET` | `/tasks/user/{user_id}` | ✅ | Tasks assigned to a user |
| `GET` | `/tasks/meeting/{meeting_id}` | ✅ | Tasks for a meeting |
| `GET` | `/dashboard/` | ✅ | Dashboard stats |
| `GET` | `/notifications/` | ✅ | Your notifications |
| `GET` | `/notifications/unread-count` | ✅ | Unread notification count |
| `PATCH` | `/notifications/{id}/read` | ✅ | Mark notification read |
| `PATCH` | `/notifications/mark-all-read` | ✅ | Mark all notifications read |

---

## Database Schema

```
users
  id, full_name, email, password_hash, team_code, created_at
  UNIQUE(email, team_code)

meetings
  id, title, transcript, uploaded_by → users.id, created_at

tasks
  id, title, description, status, priority, due_date
  assignee_id → users.id, assigned_by → users.id, meeting_id → meetings.id
  created_at, completed_at

notifications
  id, user_id → users.id, title, message, type, task_id, is_read, created_at

refresh_tokens
  id, token_hash (SHA-256), user_id → users.id, is_revoked, expires_at, created_at
```

---

## Deployment to Azure

See the full [Azure deployment guide](./docs/azure_deployment.md) for step-by-step Azure CLI commands.

**Quick summary:**
1. Push images to Azure Container Registry (ACR)
2. Create Azure Database for PostgreSQL Flexible Server
3. Deploy two Container Apps (backend + frontend)
4. Inject secrets via Azure Container App environment variables

Migrations run automatically on every container startup via `entrypoint.sh`.

---

## Contributing

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make changes and write tests
3. Run `pytest tests/ -v` and ensure all pass
4. Open a pull request

---

## License

MIT
