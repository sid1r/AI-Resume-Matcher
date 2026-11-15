
import io
import re

import pdfplumber
from docx import Document



def clean_text(text: str) -> str:
    """Clean text while preserving line breaks."""

    lines = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line)
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)



def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF."""

    extracted_text = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_text.append(page_text)

    return "\n".join(extracted_text)


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from DOCX."""

    document = Document(io.BytesIO(file_bytes))

    extracted_text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            extracted_text.append(paragraph.text)

    # Extract text from tables
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    extracted_text.append(cell.text)

    return "\n".join(extracted_text)


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    """Extract text from PDF or DOCX resume."""

    filename = filename.lower()

    if filename.endswith(".pdf"):
        text = extract_pdf_text(file_bytes)

    elif filename.endswith(".docx"):
        text = extract_docx_text(file_bytes)

    else:
        raise ValueError("Only PDF and DOCX files are supported.")

    cleaned_text = clean_text(text)

    if not cleaned_text:
        raise ValueError("No readable text found in document.")

    return cleaned_text
