"""Unit-Tests für das Chunking – laufen ohne API-Key oder Datenbank."""
import pytest

from app.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_is_single_chunk():
    text = "Ein kurzer Text."
    assert chunk_text(text, chunk_size=100, overlap=20) == [text]


def test_long_text_is_split_with_overlap():
    text = "abcdefghij" * 50  # 500 Zeichen
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    # Überlappung: Ende von Chunk 1 == Anfang von Chunk 2
    assert chunks[0][-50:] == chunks[1][:50]


def test_all_text_is_covered():
    text = "x" * 1000
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    # Letztes Zeichen muss im letzten Chunk enthalten sein
    assert sum(len(c) for c in chunks) >= 1000


def test_invalid_params_raise():
    with pytest.raises(ValueError):
        chunk_text("test", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("test", chunk_size=100, overlap=100)
