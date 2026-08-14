from app.infrastructure.database import get_db
from app.main import app
from tests.conftest import _override_get_db


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_endpoint_when_db_available(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_endpoint_when_db_unavailable(client):
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("db down")

        def close(self):
            pass

    def _broken_get_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = _broken_get_db
    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides[get_db] = _override_get_db

    assert response.status_code == 503
    assert response.json() == {"status": "not-ready"}
