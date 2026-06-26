from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document
from fastapi import HTTPException

def extract_text(
    file: UploadFile
) -> str:
    """
    Extract text from TXT, PDF and DOCX files.
    """

    filename = file.filename.lower()

    if filename.endswith(".txt"):
        text = file.file.read().decode("utf-8")
        return text
    elif filename.endswith(".md"):
        text = file.file.read().decode("utf-8")
        return text

    elif filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    elif filename.endswith(".docx"):
        document = Document(file.file)
        text = ""
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        return text

    raise HTTPException(
        status_code=400,
        detail="Only TXT, PDF and DOCX files are supported."
)