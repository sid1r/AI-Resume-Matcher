
from typing import List

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

from app.database import get_db
from app import models

from app.services.document_parser import extract_resume_text
from app.services.candidate_extractor import extract_candidate_info


router = APIRouter(
    prefix="/resumes",
    tags=["Resume Parsing"]
)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_file(filename: str):
    """Validate uploaded resume file format."""

    if not filename:
        raise ValueError("Filename is required.")

    extension = "." + filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and DOCX files are supported.")


# ----------------------------------------
# 1. Extract a single resume
# ----------------------------------------

@router.post("/extract")
async def extract_resume(file: UploadFile = File(...)):

    try:
        filename = file.filename or ""

        validate_file(filename)

        file_bytes = await file.read()

        if not file_bytes:
            raise ValueError("Uploaded file is empty.")

        text = extract_resume_text(filename, file_bytes)

        if not text.strip():
            raise ValueError("Could not extract text from this resume.")

        candidate_info = extract_candidate_info(text)

        return {
            "filename": filename,
            "candidate_information": candidate_info,
            "extracted_text": text
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not process the uploaded resume."
        )

    finally:
        await file.close()


# ----------------------------------------
# 2. Extract multiple resumes
# ----------------------------------------

@router.post("/batch-extract")
async def batch_extract_resumes(
    files: List[UploadFile] = File(...)
):

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one resume."
        )

    candidates = []
    failed_files = []

    for file in files:

        filename = file.filename or ""

        try:
            validate_file(filename)

            file_bytes = await file.read()

            if not file_bytes:
                raise ValueError("Uploaded file is empty.")

            text = extract_resume_text(filename, file_bytes)

            if not text.strip():
                raise ValueError("Could not extract text from this resume.")

            candidate_info = extract_candidate_info(text)

            candidates.append({
                "filename": filename,
                "candidate_information": candidate_info,
                "extracted_text": text
            })

        except Exception as error:

            failed_files.append({
                "filename": filename or "Unknown file",
                "error": str(error)
            })

        finally:
            await file.close()

    return {
        "total_uploaded": len(files),
        "successful": len(candidates),
        "failed": len(failed_files),
        "candidates": candidates,
        "failed_files": failed_files
    }


# ----------------------------------------
# 3. Retrieve all saved candidates
# ----------------------------------------

@router.get("/")
def get_all_candidates(
    db: Session = Depends(get_db)
):

    candidates = (
        db.query(models.Candidate)
        .order_by(models.Candidate.id.desc())
        .all()
    )

    return {
        "total_candidates": len(candidates),
        "candidates": [
            {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "phone": candidate.phone,
                "resume_filename": candidate.resume_filename,
                "candidate_information": candidate.candidate_information,
                "created_at": candidate.created_at
            }
            for candidate in candidates
        ]
    }


# ----------------------------------------
# 4. Retrieve candidate by ID
# ----------------------------------------

@router.get("/{candidate_id}")
def get_candidate_by_id(
    candidate_id: int,
    db: Session = Depends(get_db)
):

    candidate = (
        db.query(models.Candidate)
        .filter(models.Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found."
        )

    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "resume_filename": candidate.resume_filename,
        "candidate_information": candidate.candidate_information,
        "created_at": candidate.created_at
    }
