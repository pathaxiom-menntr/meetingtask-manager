# API Reference

Base URL: `http://localhost:8000` (dev) | `https://backend.YOUR_ENV.azurecontainerapps.io` (prod)

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## Authentication (`/auth`)

### `POST /auth/register`
Register a new user under a team.

**Request body**
```json
{
  "full_name": "Alice Smith",
  "email": "alice@example.com",
  "password": "SecurePass123",
  "team_code": "ACME-2024"
}
```

**Response `200`**
```json
{
  "id": 1,
  "full_name": "Alice Smith",
  "email": "alice@example.com",
  "team_code": "ACME-2024",
  "created_at": "2025-07-01T10:00:00"
}
```

**Errors**
| Status | Reason |
|---|---|
| `400` | Email already registered in this team |
| `422` | Validation error (missing fields, bad email) |

---

### `POST /auth/login`
Login and receive a token pair.

**Request body**
```json
{
  "email": "alice@example.com",
  "password": "SecurePass123",
  "team_code": "ACME-2024"
}
```

**Response `200`**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

> Store `access_token` in memory and `refresh_token` in secure storage.  
> Access token expires in 30 minutes. Refresh token expires in 7 days.

**Errors**
| Status | Reason |
|---|---|
| `401` | Invalid email, team code, or password |

---

### `POST /auth/refresh`
Rotate the refresh token. The old token is immediately revoked.

**Request body**
```json
{ "refresh_token": "eyJ..." }
```

**Response `200`** — same structure as `/auth/login`

**Errors**
| Status | Reason |
|---|---|
| `401` | Token not recognised, already revoked, or expired |

---

### `POST /auth/logout` 🔒
Revoke the refresh token server-side.

**Request body**
```json
{ "refresh_token": "eyJ..." }
```

**Response `200`**
```json
{ "message": "Logged out successfully" }
```

---

### `GET /auth/me` 🔒
Get the currently authenticated user.

**Response `200`** — same as `/auth/register` response

---

## Users (`/users`)

### `GET /users/` 🔒
List all team members (scoped to caller's team code).

**Query params**
| Param | Type | Default | Description |
|---|---|---|---|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `20` | Max results |

**Response `200`** — array of user objects

---

### `GET /users/{user_id}` 🔒
Get a user by ID.

**Response `200`** — user object  
**`404`** — user not found

---

## Meetings (`/meetings`)

### `POST /meetings/` 🔒
Create a meeting manually (no AI task extraction).

**Request body**
```json
{
  "title": "Sprint Planning Q3",
  "transcript": "Alice: We need to update the docs..."
}
```

**Response `200`**
```json
{
  "id": 5,
  "title": "Sprint Planning Q3",
  "transcript": "Alice: We need to update...",
  "uploaded_by": 1,
  "created_at": "2025-07-01T10:00:00"
}
```

---

### `POST /meetings/upload` 🔒
Upload a transcript file and auto-extract tasks via AI.

**Content-Type:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `title` | string (query param) | Meeting title |
| `file` | file | TXT, MD, PDF, or DOCX — max 10 MB, 50,000 chars |

**Response `201`**
```json
{
  "meeting": { "id": 5, "title": "...", ... },
  "tasks": [
    { "id": 10, "title": "Write release notes", "assignee_id": 2, ... }
  ],
  "skipped": [
    { "title": null, "reason": "Task title missing", "auto_assigned": false }
  ],
  "auto_assigned_tasks": [
    { "task": { ... }, "auto_assigned": true, "auto_assigned_to": "Bob Smith" }
  ]
}
```

**Errors**
| Status | Reason |
|---|---|
| `400` | Unsupported file type |
| `400` | File too large (> 10 MB) |
| `400` | Transcript too long (> 50,000 chars) |
| `400` | No readable text found |

---

### `GET /meetings/` 🔒
List meetings created by the current user.

**Query params:** `skip`, `limit`  
**Response `200`** — array of meeting objects

---

### `GET /meetings/{meeting_id}` 🔒
Get a meeting by ID (team-scoped — only visible to the uploader's teammates).

**`404`** if not found or belongs to a different team.

---

### `PUT /meetings/{meeting_id}` 🔒
Update a meeting's title or transcript. Only the creator can update.

**Request body** (all fields optional)
```json
{ "title": "Updated title", "transcript": "Updated content..." }
```

**`403`** if caller is not the meeting creator.

---

### `DELETE /meetings/{meeting_id}` 🔒
Delete a meeting. Only the creator can delete.

**Response `200`** `{ "message": "Meeting deleted successfully" }`

---

## Tasks (`/tasks`)

### Task object
```json
{
  "id": 10,
  "title": "Write release notes",
  "description": "Document the v2.0 changes",
  "status": "pending",
  "priority": "high",
  "assignee_id": 2,
  "assigned_by": 1,
  "meeting_id": 5,
  "due_date": "2025-08-01",
  "created_at": "2025-07-01T10:00:00",
  "completed_at": null
}
```

**Status values:** `pending` | `completed`  
**Priority values:** `low` | `medium` | `high` | `critical`

---

### `POST /tasks/` 🔒
Create a task manually.

**Request body**
```json
{
  "title": "Write docs",
  "description": "Update the API reference",
  "assignee_id": 2,
  "meeting_id": 5,
  "priority": "high",
  "due_date": "2025-08-01"
}
```

> `assignee_id` must be a member of the caller's team.

**Errors**
| Status | Reason |
|---|---|
| `404` | Assignee not found or not in your team |
| `404` | Meeting not found |

---

### `GET /tasks/` 🔒
List tasks where the caller is the assignee **or** the assigner.

---

### `GET /tasks/{task_id}` 🔒
Get task by ID (team-scoped).

---

### `PUT /tasks/{task_id}` 🔒
Update a task. Caller must be the assigner or assignee.

**Request body** (all fields optional)
```json
{
  "title": "New title",
  "description": "New description",
  "assignee_id": 3,
  "priority": "critical",
  "due_date": "2025-09-01"
}
```

**`403`** if caller has no relation to the task.

---

### `PATCH /tasks/{task_id}/complete` 🔒
Mark a task as completed. **Only the assignee** can complete a task.

**`403`** if caller is not the assignee.  
**`400`** if task is already completed.

---

### `DELETE /tasks/{task_id}` 🔒
Delete a task. **Only the assigner** can delete.

---

### `GET /tasks/user/{user_id}` 🔒
Get tasks assigned to a specific user (must be in same team).

---

### `GET /tasks/meeting/{meeting_id}` 🔒
Get tasks for a specific meeting (must be in same team).

---

## Dashboard (`/dashboard`)

### `GET /dashboard/` 🔒
Returns stats for the current user.

**Response `200`**
```json
{
  "total_tasks_assigned_to_me": 5,
  "completed_tasks": 2,
  "pending_tasks": 3,
  "total_tasks_i_assigned": 8,
  "overdue_tasks": 1,
  "total_meetings": 4
}
```

---

## Notifications (`/notifications`)

### `GET /notifications/` 🔒
Get notifications for the current user (newest first).

**Query params**
| Param | Default | Description |
|---|---|---|
| `limit` | `50` | Max notifications to return |

**Response `200`**
```json
[
  {
    "id": 1,
    "title": "New task assigned to you",
    "message": "Alice assigned you: \"Write release notes\"",
    "type": "task_assigned",
    "task_id": 10,
    "is_read": false,
    "created_at": "2025-07-01T10:05:00"
  }
]
```

---

### `GET /notifications/unread-count` 🔒
**Response `200`** `{ "count": 3 }`

---

### `PATCH /notifications/{notification_id}/read` 🔒
Mark a single notification as read.

---

### `PATCH /notifications/mark-all-read` 🔒
Mark all notifications as read.

**Response `200`** `{ "marked_read": 5 }`

---

## Error format

All errors return a consistent JSON body:

```json
{ "detail": "Human-readable error message" }
```

## Pagination

Endpoints that return lists support `skip` and `limit` query parameters:

```
GET /tasks/?skip=0&limit=20
GET /meetings/?skip=20&limit=20
```
