from fastapi.testclient import TestClient

from app.main import app


def test_system_status_endpoint_returns_worker_metadata() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert "worker" in payload
    assert "enabled" in payload["worker"]
