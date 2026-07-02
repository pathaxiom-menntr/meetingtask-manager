"""
Tests for AI task creation via the /meetings/upload endpoint.

We mock AIService.generate_tasks to avoid real Azure OpenAI calls in tests,
keeping tests fast, deterministic, and free.
"""
from unittest.mock import patch, MagicMock
import io

from tests.conftest import auth_headers


AI_RESPONSE_SINGLE = [
    {
        "title": "Write release notes",
        "description": "Document the changes in version 2.0",
        "assignee": "Bob Smith",
        "priority": "high",
        "due_date": "2025-08-01",
    }
]

AI_RESPONSE_NO_ASSIGNEE = [
    {
        "title": "Update readme",
        "description": None,
        "assignee": None,
        "priority": "low",
        "due_date": None,
    }
]

AI_RESPONSE_UNKNOWN_ASSIGNEE = [
    {
        "title": "Refactor auth",
        "description": "Clean up the auth module",
        "assignee": "Nonexistent Person",
        "priority": "medium",
        "due_date": None,
    }
]


def _upload(client, headers, content: str = "Alice: let's do it. Bob: agreed."):
    return client.post(
        "/meetings/upload",
        params={"title": "Sprint Planning"},
        files={"file": ("transcript.txt", io.BytesIO(content.encode()), "text/plain")},
        headers=headers,
    )


class TestAITaskCreation:
    def test_upload_creates_tasks_for_known_assignee(self, client):
        """When the assignee name matches a team member, a task is created."""
        h_alice = auth_headers(client, email="alice@t.com", password="pass1", team_code="ALPHA")
        # Register Bob so name lookup succeeds
        from tests.conftest import register_user
        register_user(client, email="bob@t.com", password="pass2",
                       full_name="Bob Smith", team_code="ALPHA")

        with patch("app.services.ai.AIService.generate_tasks", return_value=AI_RESPONSE_SINGLE):
            resp = _upload(client, h_alice)

        assert resp.status_code == 201
        data = resp.json()
        assert data["meeting"]["title"] == "Sprint Planning"
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Write release notes"
        assert len(data["skipped"]) == 0

    def test_upload_auto_assigns_when_no_assignee(self, client):
        """Tasks with no assignee are auto-assigned to least-loaded team member."""
        h = auth_headers(client, email="alice@t.com", password="pass", team_code="ALPHA")

        with patch("app.services.ai.AIService.generate_tasks", return_value=AI_RESPONSE_NO_ASSIGNEE):
            resp = _upload(client, h)

        assert resp.status_code == 201
        data = resp.json()
        assert len(data["tasks"]) == 1
        assert data["auto_assigned_tasks"][0]["auto_assigned"] is True

    def test_upload_auto_assigns_when_assignee_unknown(self, client):
        """Tasks whose assignee name can't be found are auto-assigned."""
        h = auth_headers(client, email="alice@t.com", password="pass", team_code="ALPHA")

        with patch("app.services.ai.AIService.generate_tasks", return_value=AI_RESPONSE_UNKNOWN_ASSIGNEE):
            resp = _upload(client, h)

        assert resp.status_code == 201
        data = resp.json()
        assert len(data["tasks"]) == 1
        assert data["auto_assigned_tasks"][0]["auto_assigned"] is True

    def test_upload_empty_ai_response(self, client):
        """When AI finds no tasks, response has empty tasks and skipped lists."""
        h = auth_headers(client, email="alice@t.com", password="pass", team_code="ALPHA")

        with patch("app.services.ai.AIService.generate_tasks", return_value=[]):
            resp = _upload(client, h)

        assert resp.status_code == 201
        data = resp.json()
        assert data["tasks"] == []
        assert data["skipped"] == []

    def test_upload_rejects_unsupported_file_type(self, client):
        h = auth_headers(client)
        resp = client.post(
            "/meetings/upload",
            params={"title": "Bad File"},
            files={"file": ("notes.xls", io.BytesIO(b"data"), "application/vnd.ms-excel")},
            headers=h,
        )
        assert resp.status_code == 400
        assert "supported" in resp.json()["detail"].lower()

    def test_upload_rejects_empty_transcript(self, client):
        h = auth_headers(client)
        resp = client.post(
            "/meetings/upload",
            params={"title": "Empty"},
            files={"file": ("empty.txt", io.BytesIO(b"   "), "text/plain")},
            headers=h,
        )
        assert resp.status_code == 400
        assert "no readable text" in resp.json()["detail"].lower()

    def test_upload_rejects_oversized_transcript(self, client):
        h = auth_headers(client)
        # Exceeds MAX_TRANSCRIPT_CHARS (50_000)
        huge = ("word " * 15_000).encode()  # ~75 KB of text
        resp = client.post(
            "/meetings/upload",
            params={"title": "Huge"},
            files={"file": ("big.txt", io.BytesIO(huge), "text/plain")},
            headers=h,
        )
        assert resp.status_code == 400
        assert "too long" in resp.json()["detail"].lower()

    def test_upload_requires_auth(self, client):
        resp = client.post(
            "/meetings/upload",
            params={"title": "Unauth"},
            files={"file": ("t.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert resp.status_code == 401
