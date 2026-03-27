"""Unit tests for EmbeddingService — Gemini API mocked."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from shared.exceptions import EmbeddingError
from services.embedding_service import EmbeddingService


FAKE_VECTOR = [0.1] * 3072  # gemini-embedding-001 produces 3072-dim vectors


def _make_service(embed_documents_return=None, embed_query_return=None):
    """Return an EmbeddingService with the underlying LangChain embeddings mocked."""
    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = embed_documents_return or [FAKE_VECTOR]
    mock_embeddings.embed_query.return_value = embed_query_return or FAKE_VECTOR

    with patch("services.embedding_service.get_embeddings", return_value=mock_embeddings):
        svc = EmbeddingService()
    return svc, mock_embeddings


# ---------------------------------------------------------------------------
# embed_texts
# ---------------------------------------------------------------------------

class TestEmbedTexts:
    def test_returns_list_of_vectors(self):
        svc, _ = _make_service(embed_documents_return=[FAKE_VECTOR, FAKE_VECTOR])
        result = svc.embed_texts(["hello", "world"])
        assert len(result) == 2
        assert all(isinstance(v, list) for v in result)

    def test_vector_dimension_is_correct(self):
        svc, _ = _make_service(embed_documents_return=[FAKE_VECTOR])
        result = svc.embed_texts(["test"])
        assert len(result[0]) == 3072

    def test_vector_elements_are_floats(self):
        svc, _ = _make_service(embed_documents_return=[FAKE_VECTOR])
        result = svc.embed_texts(["test"])
        assert all(isinstance(x, float) for x in result[0])

    def test_empty_input_returns_empty_list(self):
        svc, mock_emb = _make_service()
        result = svc.embed_texts([])
        assert result == []
        mock_emb.embed_documents.assert_not_called()

    def test_embed_documents_called_with_correct_texts(self):
        svc, mock_emb = _make_service(embed_documents_return=[FAKE_VECTOR, FAKE_VECTOR])
        texts = ["foo", "bar"]
        svc.embed_texts(texts)
        mock_emb.embed_documents.assert_called_once_with(texts)

    def test_api_error_raises_embedding_error(self):
        mock_embeddings = MagicMock()
        mock_embeddings.embed_documents.side_effect = RuntimeError("API down")
        with patch("services.embedding_service.get_embeddings", return_value=mock_embeddings):
            svc = EmbeddingService()
        # tenacity will retry 3 times then reraise
        with pytest.raises(EmbeddingError):
            svc.embed_texts(["test"])

    def test_single_text_returns_single_vector(self):
        svc, _ = _make_service(embed_documents_return=[FAKE_VECTOR])
        result = svc.embed_texts(["only one"])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# ping
# ---------------------------------------------------------------------------

class TestPing:
    def test_ping_success(self):
        svc, mock_emb = _make_service(embed_query_return=FAKE_VECTOR)
        svc.ping()  # should not raise
        mock_emb.embed_query.assert_called_once_with("ping")

    def test_ping_raises_embedding_error_on_failure(self):
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.side_effect = RuntimeError("unreachable")
        with patch("services.embedding_service.get_embeddings", return_value=mock_embeddings):
            svc = EmbeddingService()
        with pytest.raises(EmbeddingError):
            svc.ping()
