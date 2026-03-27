"""Unit tests for POST /api/pdf/upload — Storage and Cosmos mocked."""

from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

import fitz
import azure.functions as func
import pytest

from function_app import pdf_upload


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pdf_bytes(text: str = "Sample PDF content") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def _build_upload_request(
    file_bytes: bytes,
    filename: str = "test.pdf",
    content_type: str = "application/pdf",
) -> func.HttpRequest:
    """Build a mock multipart HttpRequest with a single 'file' field."""
    mock_file = MagicMock()
    mock_file.read.return_value = file_bytes
    mock_file.filename = filename
    mock_file.content_type = content_type

    mock_req = MagicMock(spec=func.HttpRequest)
    mock_req.files = {"file": mock_file}
    mock_req.method = "POST"
    mock_req.url = "http://localhost:7071/api/pdf/upload"
    return mock_req


def _patched_upload(file_bytes, filename="test.pdf", content_type="application/pdf"):
    """Run pdf_upload with Storage and Cosmos mocked; return (response, storage_mock, cosmos_mock)."""
    storage_mock = MagicMock()
    storage_mock.return_value.upload_pdf.return_value = (
        "https://stkaistaiagentdevkrc.blob.core.windows.net/pdfs/fake-uuid.pdf"
    )
    cosmos_mock = MagicMock()

    req = _build_upload_request(file_bytes, filename, content_type)

    with (
        patch("services.storage_service.BlobStorageService", storage_mock),
        patch("services.cosmos_service.CosmosRepository", cosmos_mock),
    ):
        resp = pdf_upload(req)

    return resp, storage_mock, cosmos_mock


# ---------------------------------------------------------------------------
# TEST-002: valid PDF → HTTP 202 + documentId
# ---------------------------------------------------------------------------

class TestPdfUploadValid:
    def test_returns_202(self):
        resp, _, _ = _patched_upload(_make_pdf_bytes())
        assert resp.status_code == 202

    def test_response_contains_document_id(self):
        resp, _, _ = _patched_upload(_make_pdf_bytes())
        body = json.loads(resp.get_body())
        assert "document_id" in body
        assert len(body["document_id"]) == 36  # UUID format

    def test_response_status_is_pending(self):
        resp, _, _ = _patched_upload(_make_pdf_bytes())
        body = json.loads(resp.get_body())
        assert body["status"] == "pending"

    def test_response_contains_file_name(self):
        resp, _, _ = _patched_upload(_make_pdf_bytes(), filename="my_report.pdf")
        body = json.loads(resp.get_body())
        assert body["file_name"] == "my_report.pdf"

    def test_storage_upload_called_once(self):
        _, storage_mock, _ = _patched_upload(_make_pdf_bytes())
        storage_mock.return_value.upload_pdf.assert_called_once()

    def test_cosmos_upsert_called_once(self):
        _, _, cosmos_mock = _patched_upload(_make_pdf_bytes())
        cosmos_mock.return_value.upsert_document.assert_called_once()

    def test_blob_name_is_uuid_based(self):
        _, storage_mock, _ = _patched_upload(_make_pdf_bytes())
        call_args = storage_mock.return_value.upload_pdf.call_args
        blob_name = call_args[0][1]  # second positional arg
        assert blob_name.endswith(".pdf")
        assert blob_name != "test.pdf"  # must not be original filename


# ---------------------------------------------------------------------------
# TEST-003: invalid MIME type → HTTP 400
# ---------------------------------------------------------------------------

class TestPdfUploadInvalidMime:
    def test_non_pdf_returns_400(self):
        resp, _, _ = _patched_upload(b"fake content", content_type="image/png")
        assert resp.status_code == 400

    def test_non_pdf_returns_error_message(self):
        resp, _, _ = _patched_upload(b"fake content", content_type="text/plain")
        body = json.loads(resp.get_body())
        assert "error" in body

    def test_storage_not_called_on_bad_mime(self):
        _, storage_mock, _ = _patched_upload(b"fake content", content_type="application/zip")
        storage_mock.return_value.upload_pdf.assert_not_called()


# ---------------------------------------------------------------------------
# No file provided → HTTP 400
# ---------------------------------------------------------------------------

class TestPdfUploadNoFile:
    def test_no_file_field_returns_400(self):
        mock_req = MagicMock(spec=func.HttpRequest)
        mock_req.files = {}

        storage_mock = MagicMock()
        cosmos_mock = MagicMock()

        with (
            patch("services.storage_service.BlobStorageService", storage_mock),
            patch("services.cosmos_service.CosmosRepository", cosmos_mock),
        ):
            resp = pdf_upload(mock_req)

        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# File too large → HTTP 413
# ---------------------------------------------------------------------------

class TestPdfUploadTooLarge:
    def test_file_over_50mb_returns_413(self):
        oversized = b"A" * (51 * 1024 * 1024)  # 51 MB

        mock_file = MagicMock()
        mock_file.read.return_value = oversized
        mock_file.filename = "huge.pdf"
        mock_file.content_type = "application/pdf"

        mock_req = MagicMock(spec=func.HttpRequest)
        mock_req.files = {"file": mock_file}

        storage_mock = MagicMock()
        cosmos_mock = MagicMock()

        with (
            patch("services.storage_service.BlobStorageService", storage_mock),
            patch("services.cosmos_service.CosmosRepository", cosmos_mock),
        ):
            resp = pdf_upload(mock_req)

        assert resp.status_code == 413
        storage_mock.return_value.upload_pdf.assert_not_called()
