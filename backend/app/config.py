"""Zentrale Konfiguration – liest alles aus Umgebungsvariablen (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://rag:rag@localhost:5432/rag"
)

# Modelle
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
# gemini-embedding-2 unterstützt 128–3072 Dimensionen. 1536 passt zur
# bestehenden chunks-Tabelle; eine Änderung erfordert ein neues Schema.
EMBEDDING_DIMENSIONS = 1536
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-3.5-flash")

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))       # Zeichen pro Chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))  # Überlappung

# Retrieval
TOP_K = int(os.getenv("TOP_K", "4"))  # Anzahl Chunks pro Anfrage
