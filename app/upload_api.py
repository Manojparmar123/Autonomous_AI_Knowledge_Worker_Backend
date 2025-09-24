# apps/backend/app/upload_api.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader
import uuid
import traceback

from .utils.vector_db import upsert_embeddings
from .utils.fallback_llm import get_embedding_with_fallback

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def safe_decode_bytes(b: bytes) -> str:
    """Decode bytes to str, ignoring invalid bytes."""
    try:
        return b.decode("utf-8")
    except Exception:
        return b.decode("utf-8", errors="ignore")


def extract_text(file_path: Path) -> str:
    """
    Extract plain text from TXT, DOCX, or PDF files.
    Returns an empty string if nothing could be extracted.
    """
    filename = file_path.name.lower()
    try:
        if filename.endswith(".txt"):
            return file_path.read_text(encoding="utf-8", errors="ignore").strip()

        if filename.endswith(".docx"):
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            return "\n".join(paragraphs).strip()

        if filename.endswith(".pdf"):
            reader = PdfReader(str(file_path))
            texts = []
            for page in reader.pages:
                ptext = page.extract_text()
                if ptext:
                    texts.append(ptext)
            return "\n".join(texts).strip()

        # unsupported type
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .docx, or .pdf")
    except HTTPException:
        raise
    except Exception:
        # fallback: try reading binary and decode safely
        try:
            raw = file_path.read_bytes()
            return safe_decode_bytes(raw)
        except Exception:
            traceback.print_exc()
            return ""


def chunk_text(text: str, chunk_size_words: int = 500) -> list[str]:
    """Split text into word-based chunks. Returns list of chunk strings."""
    if not text:
        return []
    words = text.split()
    return [" ".join(words[i : i + chunk_size_words]) for i in range(0, len(words), chunk_size_words)]


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Upload a document -> extract text -> split into chunks ->
    generate embeddings -> push to vector DB (upsert_embeddings).
    """
    try:
        # 1. Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 2. Extract text
        text_content = extract_text(file_path)
        if not text_content:
            raise HTTPException(status_code=400, detail="No text could be extracted from file")

        # 3. Chunk text
        chunks = chunk_text(text_content, chunk_size_words=500)
        if not chunks:
            raise HTTPException(status_code=400, detail="Chunking produced no chunks")

        # 4. Create embeddings + docs
        doc_id = str(uuid.uuid4())
        docs = []
        for i, chunk in enumerate(chunks):
            # Use your fallback embedding function (may raise; we catch below)
            embedding = get_embedding_with_fallback(chunk)
            docs.append(
                {
                    "doc_id": doc_id,
                    "chunk_id": f"chunk{i}",
                    "embedding": embedding,
                    "text": chunk,
                    "source": file.filename,
                }
            )

        # 5. Upsert into vector DB
        upsert_embeddings(docs)

        return {"status": "success", "filename": file.filename, "chunks_ingested": len(docs), "doc_id": doc_id}

    except HTTPException:
        # re-raise FastAPI HTTP exceptions unchanged
        raise
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
