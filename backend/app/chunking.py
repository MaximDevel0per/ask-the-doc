"""Text-Chunking: zerlegt lange Texte in überlappende Abschnitte.

Bewusst einfach gehalten – ein guter Startpunkt zum Experimentieren.
Verbesserungsideen: an Absätzen/Sätzen splitten, Token-basiert statt
Zeichen-basiert (tiktoken), semantisches Chunking.
"""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Zerlegt `text` in Chunks von `chunk_size` Zeichen mit `overlap` Überlappung.

    Die Überlappung sorgt dafür, dass Sätze an Chunk-Grenzen nicht
    "auseinandergerissen" werden und Kontext erhalten bleibt.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size muss > 0 sein")
    if overlap >= chunk_size:
        raise ValueError("overlap muss kleiner als chunk_size sein")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(text):
            break
    return chunks
