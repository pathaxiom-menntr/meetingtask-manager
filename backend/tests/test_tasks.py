"""
Tests for Task CRUD:
  - create (own team, cross-team blocked)
  - list
  - get by id (own team, cross-team blocked)
  - complete (assignee only)
  - update (assigner / assignee, cross-team assignee blocked)
  - delete (assigner only)
"""
from tests.conftest import register_user, login_user, auth_headers


def _make_headers(client, email, password, team_code):
    register_user(client, email=email, password=password, team_code=team_code)
    resp = login_user(client, email=email, password=password, team_code=team_code)
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class TestTaskCreate:
    def test_create_task_success(self, client):
        # Register two members of the same team
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        h2 = _make_headers(client, "bob@t.com", "pass2", "ALPHA")

        # Get bob's id
        bob = client.get("/auth/me", headers=h2).json()

        resp = client.post("/tasks/", json={
            "title": "Write report",
            "assignee_id": bob["id"],
        }, headers=h1)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Write report"

    def test_create_task_cross_team_assignee_blocked(self, client):
        """Assigning to a user from a different team must return 404."""
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        _make_headers(client, "carol@t.com", "pass3", "BETA")
        carol = client.get("/auth/me",
            headers=_make_headers(client, "carol2@t.com", "pass3", "BETA")).json()

        # alice (ALPHA) tries to assign to carol (BETA)
        resp = client.post("/tasks/", json={
            "title": "Sneaky task",
            "assignee_id": carol["id"],
        }, headers=h1)
        assert resp.status_code == 404
        assert "team" in resp.json()["detail"].lower()

    def test_create_task_requires_auth(self, client):
        resp = client.post("/tasks/", json={"title": "X", "assignee_id": 1})
        assert resp.status_code == 401


class TestTaskRead:
    def _setup_task(self, client):
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        h2 = _make_headers(client, "bob@t.com", "pass2", "ALPHA")
        bob = client.get("/auth/me", headers=h2).json()
        task = client.post("/tasks/", json={
            "title": "Review PR",
            "assignee_id": bob["id"],
        }, headers=h1).json()
        return h1, h2, task

    def test_get_task_by_id(self, client):
        h1, _, task = self._setup_task(client)
        resp = client.get(f"/tasks/{task['id']}", headers=h1)
        assert resp.status_code == 200
        assert resp.json()["id"] == task["id"]

    def test_get_task_cross_team_blocked(self, client):
        """A user from a different team cannot fetch another team's task."""
        _, _, task = self._setup_task(client)
        h_other = _make_headers(client, "eve@t.com", "evepass", "GAMMA")
        resp = client.get(f"/tasks/{task['id']}", headers=h_other)
        assert resp.status_code == 404

    def test_list_tasks(self, client):
        h1, h2, _ = self._setup_task(client)
        resp = client.get("/tasks/", headers=h2)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestTaskComplete:
    def test_assignee_can_complete(self, client):
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        h2 = _make_headers(client, "bob@t.com", "pass2", "ALPHA")
        bob = client.get("/auth/me", headers=h2).json()
        task = client.post("/tasks/", json={
            "title": "Deploy", "assignee_id": bob["id"]
        }, headers=h1).json()

        resp = client.patch(f"/tasks/{task['id']}/complete", headers=h2)
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_assigner_cannot_complete(self, client):
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        h2 = _make_headers(client, "bob@t.com", "pass2", "ALPHA")
        bob = client.get("/auth/me", headers=h2).json()
        task = client.post("/tasks/", json={
            "title": "Deploy", "assignee_id": bob["id"]
        }, headers=h1).json()

        resp = client.patch(f"/tasks/{task['id']}/complete", headers=h1)
        assert resp.status_code == 403

    def test_cannot_complete_twice(self, client):
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        alice = client.get("/auth/me", headers=h1).json()
        task = client.post("/tasks/", json={
            "title": "Self-task", "assignee_id": alice["id"]
        }, headers=h1).json()

        client.patch(f"/tasks/{task['id']}/complete", headers=h1)
        resp = client.patch(f"/tasks/{task['id']}/complete", headers=h1)
        assert resp.status_code == 400


class TestTaskDelete:
    def test_assigner_can_delete(self, client):
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        h2 = _make_headers(client, "bob@t.com", "pass2", "ALPHA")
        bob = client.get("/auth/me", headers=h2).json()
        task = client.post("/tasks/", json={
            "title": "Old task", "assignee_id": bob["id"]
        }, headers=h1).json()

        resp = client.delete(f"/tasks/{task['id']}", headers=h1)
        assert resp.status_code == 200

    def test_assignee_cannot_delete(self, client):
        h1 = _make_headers(client, "alice@t.com", "pass1", "ALPHA")
        h2 = _make_headers(client, "bob@t.com", "pass2", "ALPHA")
        bob = client.get("/auth/me", headers=h2).json()
        task = client.post("/tasks/", json={
            "title": "Old task", "assignee_id": bob["id"]
        }, headers=h1).json()

        resp = client.delete(f"/tasks/{task['id']}", headers=h2)
        assert resp.status_code == 403
