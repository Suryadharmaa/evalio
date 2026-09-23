from fastapi.testclient import TestClient

from api.admission_engine.config import SCHEMA_REVISION
from api.admission_engine.database.session import get_db_session
from api.index import app


def test_health_endpoint_exposes_only_public_status() -> None:
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "engine_version": "2.0.0"}


def test_readiness_checks_expected_database_revision() -> None:
    class FakeSession:
        async def scalar(self, _statement: object) -> str:
            return SCHEMA_REVISION

    async def fake_session() -> object:
        yield FakeSession()

    app.dependency_overrides[get_db_session] = fake_session
    try:
        response = TestClient(app).get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
