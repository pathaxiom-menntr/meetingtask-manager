"""
Shared pytest fixtures for all test modules.

Uses the real PostgreSQL database but wraps every test in a transaction
that is rolled back at the end — so tests are isolated and the DB stays clean.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import Base, get_db
from app.main import app

# Use the same DB as the app; each test rolls back its own transaction
engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Provide a DB session wrapped in a rolled-back transaction."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client with DB dependency overridden to use test session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Convenience helpers ────────────────────────────────────────────────────────

def register_user(client, *, email="test@example.com", password="password123",
                   full_name="Test User", team_code="TEST-TEAM"):
    return client.post("/auth/register", json={
        "full_name": full_name,
        "email": email,
        "password": password,
        "team_code": team_code,
    })


def login_user(client, *, email="test@example.com", password="password123",
               team_code="TEST-TEAM"):
    return client.post("/auth/login", json={
        "email": email,
        "password": password,
        "team_code": team_code,
    })


def auth_headers(client, *, email="test@example.com", password="password123",
                  team_code="TEST-TEAM"):
    """Register, login and return Authorization header dict."""
    register_user(client, email=email, password=password, team_code=team_code)
    resp = login_user(client, email=email, password=password, team_code=team_code)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
