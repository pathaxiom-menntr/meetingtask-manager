from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
from docx import Document

from app.core.config import settings

# Hard file-size cap (10 MB) applied before parsing to avoid memory bombs
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


def extract_text(file: UploadFile) -> str:
    """
    Extract plain text from TXT, MD, PDF and DOCX files.

    Raises:
        400 — unsupported file type, file too large, or extracted text too long.
    """
    raw = file.file.read()

    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_BYTES // (1024*1024)} MB."
        )

    filename = (file.filename or "").lower()

    if filename.endswith((".txt", ".md")):
        text = raw.decode("utf-8", errors="replace")

    elif filename.endswith(".pdf"):
        import io
        reader = PdfReader(io.BytesIO(raw))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    elif filename.endswith(".docx"):
        import io
        document = Document(io.BytesIO(raw))
        text = "\n".join(
            p.text for p in document.paragraphs if p.text.strip()
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Only TXT, MD, PDF and DOCX files are supported."
        )

    # Guard against huge transcripts that would exceed AI token limits / cost budgets
    if len(text) > settings.MAX_TRANSCRIPT_CHARS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Transcript is too long ({len(text):,} characters). "
                f"Maximum allowed is {settings.MAX_TRANSCRIPT_CHARS:,} characters. "
                "Please trim the transcript before uploading."
            )
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text could be extracted from the uploaded file."
        )

    return text