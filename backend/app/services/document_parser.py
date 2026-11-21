
import io
import re

import pdfplumber
from docx import Document


TECH_TERMS = [
    "FastAPI",
    "PostgreSQL",
    "Scikit-learn",
    "JavaScript",
    "MySQL",
    "MongoDB",
    "Django",
    "Docker",
    "Python",
    "Flask",
    "React",
    "AWS",
    "Linux",
    "Kubernetes",
    "TensorFlow",
    "PyTorch",
    "GitHub",
    "REST API",
]

SECTION_HEADINGS = [
    "PROFESSIONAL SUMMARY",
    "WORK EXPERIENCE",
    "EDUCATION",
    "TECHNICAL SKILLS",
    "FUNCTIONAL SKILLS",
    "PROJECTS",
    "CERTIFICATIONS",
]


def normalize_text(text: str) -> str:
    """Fix common joined words while preserving technical terms."""

    # Add missing spaces before known technical terms.
    for term in TECH_TERMS:
        pattern = r"([a-z])(" + re.escape(term) + r")"

        text = re.sub(
            pattern,
            r"\1 \2",
            text,
            flags=re.IGNORECASE
        )

    # Add missing spaces after technical terms.
    # Preserve plural forms such as REST APIs.
    for term in TECH_TERMS:
        pattern = (
            r"(" + re.escape(term) + r")"
            r"(?=[a-z]{2,})"
        )

        text = re.sub(
            pattern,
            r"\1 ",
            text,
            flags=re.IGNORECASE
        )

    # Separate section headings from preceding text.
    for heading in SECTION_HEADINGS:
        pattern = r"\s*(?=" + re.escape(heading) + r"\b)"

        text = re.sub(
            pattern,
            "\n",
            text,
            flags=re.IGNORECASE
        )

    return text


def clean_text(text: str) -> str:
    """Clean extracted text while preserving line breaks."""

    lines = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line)
        line = line.strip()

        if line:
            lines.append(line)

    cleaned_text = "\n".join(lines)

    cleaned_text = normalize_text(cleaned_text)

    # Clean spacing after normalization.
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n{2,}", "\n", cleaned_text)

    return cleaned_text.strip()


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF."""

    extracted_text = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

        # Correct iteration: use pdf.pages
        for page in pdf.pages:
            page_text = page.extract_text(
                x_tolerance=2,
                y_tolerance=3
            )

            if page_text:
                extracted_text.append(page_text)

    return "\n".join(extracted_text)


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from DOCX."""

    document = Document(io.BytesIO(file_bytes))
    extracted_text = []

    # Extract paragraphs.
    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            extracted_text.append(paragraph.text)

    # Extract tables.
    for table in document.tables:

        for row in table.rows:

            row_text = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if row_text:
                extracted_text.append(" | ".join(row_text))

    return "\n".join(extracted_text)


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    """Extract text from PDF or DOCX resume."""

    filename = filename.lower()

    if filename.endswith(".pdf"):
        text = extract_pdf_text(file_bytes)

    elif filename.endswith(".docx"):
        text = extract_docx_text(file_bytes)

    else:
        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

    cleaned_text = clean_text(text)

    if not cleaned_text:
        raise ValueError(
            "No readable text found in document."
        )

    return cleaned_text
