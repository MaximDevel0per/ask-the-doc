"""Datenbankzugriff: Postgres + pgvector.

Verwaltet Dokumente und deren Chunks inkl. Embedding-Vektoren.
"""
import psycopg
from pgvector.psycopg import register_vector

from app import config


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(config.DATABASE_URL)
    register_vector(conn)
    return conn


def init_db() -> None:
    """Erstellt Extension und Tabellen beim App-Start (idempotent)."""
    with psycopg.connect(config.DATABASE_URL) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now()
            )
            """
        )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id INT REFERENCES documents(id) ON DELETE CASCADE,
                chunk_index INT NOT NULL,
                content TEXT NOT NULL,
                embedding vector({config.EMBEDDING_DIMENSIONS})
            )
            """
        )
        # Index für schnelle Ähnlichkeitssuche (Cosine Distance)
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS chunks_embedding_idx
            ON chunks USING hnsw (embedding vector_cosine_ops)
            """
        )
        conn.commit()


def insert_document(filename: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO documents (filename) VALUES (%s) RETURNING id",
            (filename,),
        ).fetchone()
        conn.commit()
        return row[0]


def insert_chunks(document_id: int, chunks: list[str], embeddings: list) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            for i, (content, embedding) in enumerate(zip(chunks, embeddings)):
                cur.execute(
                    """
                    INSERT INTO chunks (document_id, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (document_id, i, content, embedding),
                )
        conn.commit()


def list_documents() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.filename, d.created_at, count(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id ORDER BY d.created_at DESC
            """
        ).fetchall()
    return [
        {"id": r[0], "filename": r[1], "created_at": str(r[2]), "chunks": r[3]}
        for r in rows
    ]


def delete_document(document_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        conn.commit()


def search_similar_chunks(query_embedding, top_k: int) -> list[dict]:
    """Findet die ähnlichsten Chunks per Cosine Distance (Operator <=>)."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.content, d.filename, c.chunk_index,
                   1 - (c.embedding <=> %s::vector) AS similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k),
        ).fetchall()
    return [
        {
            "content": r[0],
            "filename": r[1],
            "chunk_index": r[2],
            "similarity": round(float(r[3]), 4),
        }
        for r in rows
    ]
