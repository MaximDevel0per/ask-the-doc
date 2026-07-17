# Ask The Doc – Chat mit deinen Dokumenten

Ein RAG-Projekt (Retrieval-Augmented Generation) als Lern- und Portfolio-Projekt:
Dokumente (PDF/TXT/MD) hochladen und Fragen zu deren Inhalt stellen.

**Stack:** Python · FastAPI · PostgreSQL + pgvector · Gemini API · React (Vite) · Docker · GitHub Actions

## Wie es funktioniert

```
Upload:  Datei → Text extrahieren → Chunks → Embeddings → pgvector
Frage:   Frage → Embedding → ähnlichste Chunks suchen → LLM antwortet mit Kontext + Quellen
```
<img width="1313" height="1083" alt="image" src="https://github.com/user-attachments/assets/4ca3c3ca-a432-4499-89c8-dfa3f7960566" />

| Datei | Verantwortung |
|---|---|
| `backend/app/ingestion.py` | Datei einlesen, Text extrahieren, Pipeline orchestrieren |
| `backend/app/chunking.py` | Text in überlappende Abschnitte zerlegen |
| `backend/app/embeddings.py` | Texte in Vektoren umwandeln (Gemini) |
| `backend/app/db.py` | Postgres/pgvector: Speichern + Ähnlichkeitssuche |
| `backend/app/chat.py` | Retrieval + LLM-Antwort mit Quellenangabe |
| `backend/app/main.py` | FastAPI-Endpoints |

## Setup

Voraussetzungen: Docker Desktop, Node.js ≥ 20, ein [Google-API-Key](https://aistudio.google.com/apikey)

```bash
# 1. API-Key hinterlegen
cp .env.example .env        # dann GOOGLE_API_KEY in .env eintragen

# 2. Datenbank + Backend starten
docker compose up --build

# 3. Frontend starten (zweites Terminal)
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- API-Doku (Swagger): http://localhost:8000/docs

### Backend lokal ohne Docker (optional)

```bash
docker compose up db        # nur die Datenbank
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests

```bash
cd backend
pytest -v
```

Die CI (GitHub Actions) führt bei jedem Push Tests, Frontend-Build und Docker-Build aus.

## Kosten

Für Experimente in dieser Größenordnung reicht in der Regel das kostenlose
Kontingent von Google AI Studio. Aktuelle Limits und Preise:
[ai.google.dev/pricing](https://ai.google.dev/pricing).

Die Embedding-Dimension ist in `config.py` auf 1536 gesetzt, passend zur
`chunks`-Tabelle. Wer sie ändert, muss die Tabelle neu anlegen und alle
Dokumente erneut hochladen.

## Ausbau-Ideen (Roadmap fürs Portfolio)

- [ ] Deployment auf Azure (App Service oder Container Apps) – passt zu deinem Profil
- [ ] Streaming-Antworten (Server-Sent Events)
- [ ] Besseres Chunking (satzbasiert oder token-basiert mit `tiktoken`)
- [ ] Hybrid Search (Vektor + Volltextsuche kombinieren)
- [ ] Chat-Historie (Folgefragen mit Konversationskontext)
- [ ] Auth (JWT – kennst du schon aus dem Berufsalltag)
- [ ] Evaluation: Antwortqualität messen (z. B. mit RAGAS)
