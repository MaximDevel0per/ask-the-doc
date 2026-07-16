"""FastAPI-App: REST-Endpoints für Upload, Dokumentliste und Chat.

Swagger-UI zum Testen: http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.genai import errors
from pydantic import BaseModel

from app import db
from app.chat import answer_question
from app.ingestion import ingest_file

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()  # Tabellen beim Start anlegen
    yield


app = FastAPI(title="RAG Starter", lifespan=lifespan)

# CORS: erlaubt Zugriff vom Vite-Dev-Server (Port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/documents")
async def upload_document(file: UploadFile):
    """Lädt ein Dokument hoch und startet die Ingestion-Pipeline."""
    data = await file.read()
    try:
        return ingest_file(file.filename, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except errors.APIError as e:
        logging.exception("Embedding-Aufruf fehlgeschlagen")
        raise HTTPException(status_code=502, detail=f"Gemini-Fehler: {e.message}")


@app.get("/api/documents")
def get_documents():
    return db.list_documents()


@app.delete("/api/documents/{document_id}")
def remove_document(document_id: int):
    db.delete_document(document_id)
    return {"deleted": document_id}


@app.post("/api/chat")
def chat(request: ChatRequest):
    """Beantwortet eine Frage auf Basis der hochgeladenen Dokumente."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Frage darf nicht leer sein")
    try:
        return answer_question(request.question)
    except errors.APIError as e:
        logging.exception("Chat-Aufruf fehlgeschlagen")
        raise HTTPException(status_code=502, detail=f"Gemini-Fehler: {e.message}")
