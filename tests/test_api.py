import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from doc_to_md.api import app


client = TestClient(app)


def test_api_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_conversion_engines_endpoint() -> None:
    response = client.get("/apps/conversion/engines")
    assert response.status_code == 200
    payload = response.json()
    assert "engines" in payload
    assert "local" in payload["engines"]
