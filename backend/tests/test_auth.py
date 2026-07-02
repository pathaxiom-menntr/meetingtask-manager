"""
Tests for authentication flows:
  - register
  - login (correct / wrong credentials / wrong team)
  - token refresh with rotation
  - logout (token revocation)
  - /auth/me
"""
from tests.conftest import register_user, login_user, auth_headers


# ── Registration ──────────────────────────────────────────────────────────────

class TestRegister:
    def test_register_success(self, client):
        resp = register_user(client)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["team_code"] == "TEST-TEAM"
        assert "password_hash" not in data

    def test_register_duplicate_in_same_team(self, client):
        register_user(client)
        resp = register_user(client)  # same email + same team
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_same_email_different_team(self, client):
        """Same email can register in a different team."""
        register_user(client, team_code="TEAM-A")
        resp = register_user(client, team_code="TEAM-B")
        assert resp.status_code == 200

    def test_register_missing_team_code(self, client):
        resp = client.post("/auth/register", json={
            "full_name": "Jane",
            "email": "jane@example.com",
            "password": "secret123",
        })
        assert resp.status_code == 422  # validation error


# ── Login ─────────────────────────────────────────────────────────────────────

class TestLogin:
    def test_login_success(self, client):
        register_user(client)
        resp = login_user(client)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        register_user(client)
        resp = login_user(client, password="wrongpassword")
        assert resp.status_code == 401

    def test_login_wrong_team_code(self, client):
        register_user(client, team_code="RIGHT-TEAM")
        resp = login_user(client, team_code="WRONG-TEAM")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = login_user(client, email="nobody@example.com")
        assert resp.status_code == 401


# ── Token refresh and rotation ────────────────────────────────────────────────

class TestRefresh:
    def test_refresh_issues_new_tokens(self, client):
        register_user(client)
        login_resp = login_user(client)
        old_refresh = login_resp.json()["refresh_token"]

        resp = client.post("/auth/refresh", json={"refresh_token": old_refresh})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["refresh_token"] != old_refresh  # token was rotated

    def test_old_refresh_token_rejected_after_rotation(self, client):
        """After a refresh, the old token must be revoked."""
        register_user(client)
        login_resp = login_user(client)
        old_refresh = login_resp.json()["refresh_token"]

        # Rotate once
        client.post("/auth/refresh", json={"refresh_token": old_refresh})

        # Attempt to reuse the old token — should be rejected
        resp = client.post("/auth/refresh", json={"refresh_token": old_refresh})
        assert resp.status_code == 401

    def test_invalid_refresh_token_rejected(self, client):
        resp = client.post("/auth/refresh", json={"refresh_token": "not.a.real.token"})
        assert resp.status_code == 401


# ── Logout / revocation ───────────────────────────────────────────────────────

class TestLogout:
    def test_logout_revokes_token(self, client):
        register_user(client)
        login_resp = login_user(client)
        access = login_resp.json()["access_token"]
        refresh = login_resp.json()["refresh_token"]
        headers = {"Authorization": f"Bearer {access}"}

        # Logout
        resp = client.post("/auth/logout", json={"refresh_token": refresh}, headers=headers)
        assert resp.status_code == 200

        # Refresh should now fail
        resp2 = client.post("/auth/refresh", json={"refresh_token": refresh})
        assert resp2.status_code == 401


# ── /auth/me ──────────────────────────────────────────────────────────────────

class TestMe:
    def test_me_returns_current_user(self, client):
        headers = auth_headers(client)
        resp = client.get("/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_me_requires_auth(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401
