"""Chat: Retrieval + Generation.

Der Kern von RAG: Die Frage wird eingebettet, ähnliche Chunks werden
aus der Vektordatenbank geholt und dem LLM als Kontext mitgegeben.
"""
from app import config, db
from app.embeddings import embed_query, get_client

SYSTEM_PROMPT = """Du bist ein hilfreicher Assistent, der Fragen zu \
Dokumenten beantwortet. Antworte NUR auf Basis des bereitgestellten \
Kontexts. Wenn die Antwort nicht im Kontext steht, sage das ehrlich. \
Nenne am Ende die Quelle(n) (Dateiname), auf die du dich stützt."""


def answer_question(question: str) -> dict:
    # 1. Retrieval: ähnlichste Chunks zur Frage finden
    query_embedding = embed_query(question)
    sources = db.search_similar_chunks(query_embedding, config.TOP_K)

    if not sources:
        return {
            "answer": "Es wurden noch keine Dokumente hochgeladen.",
            "sources": [],
        }

    # 2. Kontext für das LLM zusammenbauen
    context = "\n\n---\n\n".join(
        f"[Quelle: {s['filename']}, Abschnitt {s['chunk_index']}]\n{s['content']}"
        for s in sources
    )

    # 3. Generation: LLM beantwortet die Frage anhand des Kontexts
    interaction = get_client().interactions.create(
        model=config.CHAT_MODEL,
        system_instruction=SYSTEM_PROMPT,
        input=f"Kontext:\n{context}\n\nFrage: {question}",
    )

    return {
        "answer": interaction.output_text,
        "sources": [
            {
                "filename": s["filename"],
                "chunk_index": s["chunk_index"],
                "similarity": s["similarity"],
            }
            for s in sources
        ],
    }
