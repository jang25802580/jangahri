"""Unit tests for GET /api/health — Azure services mocked."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import azure.functions as func
import pytest

from function_app import health


def _build_request() -> func.HttpRequest:
    return func.HttpRequest(
        method="GET",
        url="http://localhost:7071/api/health",
        body=b"",
        params={},
        headers={},
        route_params={},
    )


def _all_ok_patches():
    """Context managers that make every service ping succeed."""
    return [
        patch("function_app.BlobStorageService"),
        patch("function_app.CosmosRepository"),
        patch("function_app.EmbeddingService"),
    ]


# ---------------------------------------------------------------------------
# TEST-001: all services healthy → 200
# ---------------------------------------------------------------------------

class TestHealthAllOk:
    def test_status_healthy(self):
        with (
            patch("services.storage_service.BlobStorageService") as mock_s,
            patch("services.cosmos_service.CosmosRepository") as mock_c,
            patch("services.embedding_service.EmbeddingService") as mock_e,
        ):
            mock_s.return_value.ping.return_value = None
            mock_c.return_value.ping.return_value = None
            mock_e.return_value.ping.return_value = None

            req = _build_request()
            resp = health(req)

        body = json.loads(resp.get_body())
        assert resp.status_code == 200
        assert body["status"] == "healthy"
        assert body["checks"]["storage"] == "ok"
        assert body["checks"]["cosmos"] == "ok"
        assert body["checks"]["gemini"] == "ok"

    def test_content_type_is_json(self):
        with (
            patch("services.storage_service.BlobStorageService"),
            patch("services.cosmos_service.CosmosRepository"),
            patch("services.embedding_service.EmbeddingService"),
        ):
            req = _build_request()
            resp = health(req)

        assert "application/json" in (resp.mimetype or "")


# ---------------------------------------------------------------------------
# TEST: individual service failure → 503 degraded
# ---------------------------------------------------------------------------

class TestHealthDegraded:
    def _run_health_with_failures(self, fail_storage=False, fail_cosmos=False, fail_gemini=False):
        storage_mock = MagicMock()
        cosmos_mock = MagicMock()
        gemini_mock = MagicMock()

        if fail_storage:
            storage_mock.return_value.ping.side_effect = RuntimeError("storage down")
        if fail_cosmos:
            cosmos_mock.return_value.ping.side_effect = RuntimeError("cosmos down")
        if fail_gemini:
            gemini_mock.return_value.ping.side_effect = RuntimeError("gemini down")

        with (
            patch("services.storage_service.BlobStorageService", storage_mock),
            patch("services.cosmos_service.CosmosRepository", cosmos_mock),
            patch("services.embedding_service.EmbeddingService", gemini_mock),
        ):
            req = _build_request()
            return health(req)

    def test_storage_down_returns_503(self):
        resp = self._run_health_with_failures(fail_storage=True)
        assert resp.status_code == 503
        body = json.loads(resp.get_body())
        assert body["status"] == "degraded"
        assert body["checks"]["storage"] == "unavailable"

    def test_cosmos_down_returns_503(self):
        resp = self._run_health_with_failures(fail_cosmos=True)
        assert resp.status_code == 503
        body = json.loads(resp.get_body())
        assert body["checks"]["cosmos"] == "unavailable"

    def test_gemini_down_returns_503(self):
        resp = self._run_health_with_failures(fail_gemini=True)
        assert resp.status_code == 503
        body = json.loads(resp.get_body())
        assert body["checks"]["gemini"] == "unavailable"

    def test_all_down_returns_503(self):
        resp = self._run_health_with_failures(
            fail_storage=True, fail_cosmos=True, fail_gemini=True
        )
        assert resp.status_code == 503
        body = json.loads(resp.get_body())
        assert body["status"] == "degraded"
