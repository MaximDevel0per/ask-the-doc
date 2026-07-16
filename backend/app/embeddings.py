"""Embeddings über die Gemini-API.

Ein Embedding ist ein Zahlenvektor, der die Bedeutung eines Textes
repräsentiert. Ähnliche Texte haben ähnliche Vektoren – darauf basiert
die semantische Suche.
"""
import functools

from google import genai
from google.genai import types

from app import config


@functools.cache
def get_client() -> genai.Client:
    """Client erst beim ersten Aufruf bauen.

    genai.Client() wirft sofort, wenn der Key fehlt – auf Modulebene würde
    das die ganze App am Start abstürzen lassen statt nur diesen Aufruf.
    """
    if not config.GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY fehlt. Key erstellen unter "
            "https://aistudio.google.com/apikey und in die .env eintragen."
        )
    return genai.Client(api_key=config.GOOGLE_API_KEY)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Erzeugt Embeddings für mehrere Texte in einem API-Call (Batch)."""
    # Jeder Text muss ein eigenes Content-Objekt sein. Eine flache Liste von
    # Strings fasst gemini-embedding-2 zu EINEM Embedding zusammen.
    response = get_client().models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=[
            types.Content(parts=[types.Part.from_text(text=t)]) for t in texts
        ],
        config=types.EmbedContentConfig(
            output_dimensionality=config.EMBEDDING_DIMENSIONS
        ),
    )
    return [item.values for item in response.embeddings]


def embed_query(text: str) -> list[float]:
    """Erzeugt das Embedding für eine einzelne Nutzerfrage.

    gemini-embedding-2 kennt keinen `task_type`-Parameter mehr; die Absicht
    wird stattdessen als Instruktion vorangestellt.
    """
    return embed_texts([f"task: search result | query: {text}"])[0]
