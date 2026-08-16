import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://pocketledger:pocketledger@localhost:5433/pocketledger_test",
)

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False
)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE transactions, categories, users RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    from app.api import middleware as middleware_module

    yield
    if hasattr(middleware_module, "_rate_limiter_attempts"):
        middleware_module._rate_limiter_attempts.clear()


def _override_get_db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_and_login(
    client, name="Alice", email="alice@example.com", password="supersecret123"
):
    client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client):
    return register_and_login(client)


@pytest.fixture
def other_auth_headers(client):
    return register_and_login(
        client, name="Bob", email="bob@example.com", password="supersecret123"
    )
