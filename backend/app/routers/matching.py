
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.document_parser import extract_resume_text
from app.services.candidate_extractor import extract_candidate_info
from app.services.jd_parser import analyze_job_description
from app.services.matching_service import calculate_matching_score


router = APIRouter(
    prefix="/matching",
    tags=["AI Resume Matching"]
)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/batch")
async def match_resumes(
    jd_text: str = Form(...),
    files: List[UploadFile] = File(...)
):

    if not jd_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one resume."
        )

    # Analyze the job description once
    try:
        jd_requirements = analyze_job_description(jd_text)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    results = []
    failed_files = []

    for file in files:

        filename = file.filename or ""

        try:
            extension = "." + filename.rsplit(".", 1)[-1].lower()

            if extension not in ALLOWED_EXTENSIONS:
                raise ValueError("Only PDF and DOCX files are supported.")

            file_bytes = await file.read()

            if not file_bytes:
                raise ValueError("Uploaded file is empty.")

            # Extract resume text
            resume_text = extract_resume_text(
                filename,
                file_bytes
            )

            # Extract candidate information
            candidate_info = extract_candidate_info(resume_text)

            # Calculate matching score
            match_result = calculate_matching_score(
                resume_text,
                candidate_info,
                jd_text,
                jd_requirements
            )

            results.append({
                "filename": filename,
                "candidate_information": candidate_info,
                "matching_analysis": match_result
            })

        except Exception as error:

            failed_files.append({
                "filename": filename or "Unknown file",
                "error": str(error)
            })

        finally:
            await file.close()

    # Rank candidates by overall score
    results.sort(
        key=lambda candidate: candidate["matching_analysis"][
            "overall_matching_score"
        ],
        reverse=True
    )

    # Assign ranking positions
    for rank, candidate in enumerate(results, start=1):
        candidate["rank"] = rank

    return {
        "job_requirements": jd_requirements,
        "total_uploaded": len(files),
        "successful": len(results),
        "failed": len(failed_files),
        "ranked_candidates": results,
        "failed_files": failed_files
    }
