"""Ingestion: Datei -> Text -> Chunks -> Embeddings -> Datenbank."""
import io
import logging

from pypdf import PdfReader

from app import config, db
from app.chunking import chunk_text
from app.embeddings import embed_texts

logger = logging.getLogger(__name__)


def extract_text(filename: str, data: bytes) -> str:
    """Extrahiert Text aus PDF-, TXT- oder Markdown-Dateien."""
    name = filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="replace")
    raise ValueError(f"Nicht unterstütztes Dateiformat: {filename}")


def ingest_file(filename: str, data: bytes) -> dict:
    """Komplette Ingestion-Pipeline für eine hochgeladene Datei."""
    text = extract_text(filename, data)
    chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    if not chunks:
        raise ValueError("Kein Text in der Datei gefunden")

    logger.info("Ingestion: %s -> %d Chunks", filename, len(chunks))
    embeddings = embed_texts(chunks)

    document_id = db.insert_document(filename)
    db.insert_chunks(document_id, chunks, embeddings)
    return {"document_id": document_id, "filename": filename, "chunks": len(chunks)}
