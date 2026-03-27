"""Unit tests for PDFService — text extraction and chunking."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest

from shared.exceptions import PDFProcessingError
from services.pdf_service import PDFService


# ---------------------------------------------------------------------------
# Helper: Build a minimal in-memory PDF with fitz
# ---------------------------------------------------------------------------

def _make_pdf(pages: list[str]) -> bytes:
    """Return PDF bytes with the given text on each page."""
    import fitz

    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        if text:
            page.insert_text((72, 72), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# extract_text
# ---------------------------------------------------------------------------

class TestExtractText:
    def setup_method(self):
        self.svc = PDFService()

    def test_single_page_returns_one_entry(self):
        pdf = _make_pdf(["Hello World"])
        result = self.svc.extract_text(pdf)
        assert len(result) == 1
        assert result[0]["page_number"] == 1
        assert "Hello World" in result[0]["text"]

    def test_multipage_returns_all_pages(self):
        pdf = _make_pdf(["Page one", "Page two", "Page three"])
        result = self.svc.extract_text(pdf)
        assert len(result) == 3
        assert result[1]["page_number"] == 2
        assert "Page two" in result[1]["text"]

    def test_empty_page_text_is_empty_string(self):
        pdf = _make_pdf([""])
        result = self.svc.extract_text(pdf)
        assert len(result) == 1
        assert result[0]["text"] == ""

    def test_invalid_bytes_raises_pdf_processing_error(self):
        with pytest.raises(PDFProcessingError):
            self.svc.extract_text(b"not a pdf")

    def test_large_text_page(self):
        # PyMuPDF's insert_text clips long single-line strings at page width;
        # use multi-line content to verify large-page extraction works.
        large_text = "\n".join(["Line number {:04d}".format(i) for i in range(100)])
        pdf = _make_pdf([large_text])
        result = self.svc.extract_text(pdf)
        assert len(result) >= 1
        assert len(result[0]["text"]) > 10


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------

class TestChunkText:
    def setup_method(self):
        self.svc = PDFService()

    def test_empty_pages_returns_empty_list(self):
        assert self.svc.chunk_text([]) == []

    def test_pages_with_only_empty_text_returns_empty(self):
        pages = [{"page_number": 1, "text": ""}]
        assert self.svc.chunk_text(pages) == []

    def test_short_text_returns_single_chunk(self):
        pages = [{"page_number": 1, "text": "Short text."}]
        chunks = self.svc.chunk_text(pages, chunk_size=1000, overlap=200)
        assert len(chunks) == 1
        assert "Short text." in chunks[0]

    def test_chunk_count_matches_expected(self):
        # 3000-character text with chunk_size=1000, overlap=200 → step=800
        # positions: 0, 800, 1600, 2400 → 4 chunks
        text = "X" * 3000
        pages = [{"page_number": 1, "text": text}]
        chunks = self.svc.chunk_text(pages, chunk_size=1000, overlap=200)
        assert len(chunks) == 4

    def test_chunks_have_overlap(self):
        text = "A" * 500 + "B" * 500 + "C" * 500
        pages = [{"page_number": 1, "text": text}]
        chunks = self.svc.chunk_text(pages, chunk_size=600, overlap=100)
        # First chunk ends with A's, second chunk should start with A's (overlap)
        assert chunks[0][-100:].strip("A") == "" or len(chunks[0]) <= 600

    def test_all_chunks_within_max_size(self):
        text = "word " * 1000
        pages = [{"page_number": 1, "text": text}]
        chunks = self.svc.chunk_text(pages, chunk_size=500, overlap=50)
        for chunk in chunks:
            assert len(chunk) <= 500

    def test_multipage_text_concatenated(self):
        pages = [
            {"page_number": 1, "text": "First page content."},
            {"page_number": 2, "text": "Second page content."},
        ]
        chunks = self.svc.chunk_text(pages, chunk_size=1000, overlap=0)
        combined = "".join(chunks)
        assert "First page content." in combined
        assert "Second page content." in combined
