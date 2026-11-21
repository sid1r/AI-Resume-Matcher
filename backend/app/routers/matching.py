
from typing import List, Optional


from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends
)
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

from app.services.document_parser import extract_resume_text
from app.services.candidate_extractor import extract_candidate_info
from app.services.matching_service import calculate_matching_score
from app.services.jd_parser import analyze_job_description


router = APIRouter(
    prefix="/matching",
    tags=["AI Resume Matching"]
)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/batch")
async def match_resumes(
    files: List[UploadFile] = File(...),
    jd_id: Optional[int] = Form(None),
    jd_text: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # ----------------------------------------
    # 1. Validate uploaded files
    # ----------------------------------------

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one resume."
        )

    # ----------------------------------------
    # 2. Get or create Job Description
    # ----------------------------------------

    if jd_id is not None:

        job_description = (
            db.query(models.JobDescription)
            .filter(models.JobDescription.id == jd_id)
            .first()
        )

        if not job_description:
            raise HTTPException(
                status_code=404,
                detail="Job description not found."
            )

        jd_text = str(job_description.jd_text)
        jd_requirements = job_description.requirements

    elif jd_text and jd_text.strip():

        jd_text = jd_text.strip()

        try:
            jd_requirements = analyze_job_description(jd_text)

            job_description = models.JobDescription(
                title=title or "Untitled Job Description",
                jd_text=jd_text,
                requirements=jd_requirements
            )

            db.add(job_description)
            db.flush()

        except Exception as error:
            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=f"Could not analyze job description: {str(error)}"
            )

    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide either jd_id or jd_text."
        )

    results = []
    failed_files = []

    # ----------------------------------------
    # 3. Extract and process resumes
    # ----------------------------------------

    for file in files:

        filename = file.filename or "Unknown file"

        try:
            extension = "." + filename.rsplit(".", 1)[-1].lower()

            if extension not in ALLOWED_EXTENSIONS:
                raise ValueError(
                    "Only PDF and DOCX files are supported."
                )

            file_bytes = await file.read()

            if not file_bytes:
                raise ValueError("Uploaded file is empty.")

            resume_text = extract_resume_text(
                filename,
                file_bytes
            )

            if not resume_text or not resume_text.strip():
                raise ValueError(
                    "Could not extract text from this resume."
                )

            candidate_info = extract_candidate_info(resume_text)

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

            print(f"Successfully processed: {filename}")

        except Exception as error:

            failed_files.append({
                "filename": filename,
                "error": str(error)
            })

            print(f"Failed to process {filename}: {error}")

        finally:
            await file.close()

    # ----------------------------------------
    # 4. Rank candidates
    # ----------------------------------------

    results.sort(
        key=lambda item: float(
            item["matching_analysis"].get(
                "overall_matching_score", 0
            )
        ),
        reverse=True
    )

    # ----------------------------------------
    # 5. Save candidates and matching results
    # ----------------------------------------

    try:

        for rank, candidate_result in enumerate(results, start=1):

            candidate_info = candidate_result[
                "candidate_information"
            ]

            matching_analysis = candidate_result[
                "matching_analysis"
            ]

            email = candidate_info.get("email")

            candidate_record = None

            if email:
                candidate_record = (
                    db.query(models.Candidate)
                    .filter(models.Candidate.email == email)
                    .first()
                )

            if candidate_record is None:

                candidate_record = models.Candidate(
                    name=candidate_info.get("name"),
                    email=email,
                    phone=candidate_info.get("phone"),
                    resume_filename=candidate_result["filename"],
                    candidate_information=candidate_info
                )

                db.add(candidate_record)

            else:

                candidate_record.name = candidate_info.get("name")
                candidate_record.phone = candidate_info.get("phone")
                candidate_record.resume_filename = (
                    candidate_result["filename"]
                )
                candidate_record.candidate_information = candidate_info

            db.flush()

            matching_record = models.MatchingResult(
                candidate_id=candidate_record.id,
                job_description_id=job_description.id,
                overall_matching_score=float(
                    matching_analysis["overall_matching_score"]
                ),
                rank=rank,
                matching_analysis=matching_analysis
            )

            db.add(matching_record)
            db.flush()

            candidate_result["rank"] = rank
            candidate_result["candidate_id"] = candidate_record.id
            candidate_result["matching_result_id"] = matching_record.id

        db.commit()

    except Exception as error:

        db.rollback()

        print("Database saving error:", str(error))

        raise HTTPException(
            status_code=500,
            detail="Failed to save matching results. Check backend logs."
        )

    # ----------------------------------------
    # 6. Return batch response
    # ----------------------------------------

    return {
        "job_description_id": job_description.id,
        "job_title": job_description.title,
        "job_requirements": jd_requirements,
        "total_uploaded": len(files),
        "successful": len(results),
        "failed": len(failed_files),
        "ranked_candidates": results,
        "failed_files": failed_files
    }


# ----------------------------------------
# 7. Retrieve matching results by JD ID
# ----------------------------------------

@router.get("/results/{jd_id}")
def get_matching_results(
    jd_id: int,
    db: Session = Depends(get_db)
):

    job_description = (
        db.query(models.JobDescription)
        .filter(models.JobDescription.id == jd_id)
        .first()
    )

    if not job_description:
        raise HTTPException(
            status_code=404,
            detail="Job description not found."
        )

    matching_results = (
        db.query(models.MatchingResult)
        .filter(
            models.MatchingResult.job_description_id == jd_id
        )
        .order_by(models.MatchingResult.rank.asc())
        .all()
    )

    results = []

    for result in matching_results:

        candidate = result.candidate

        results.append({
            "matching_result_id": result.id,
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "email": candidate.email,
            "resume_filename": candidate.resume_filename,
            "overall_matching_score": result.overall_matching_score,
            "rank": result.rank,
            "matching_analysis": result.matching_analysis
        })

    return {
        "job_description_id": jd_id,
        "job_title": job_description.title,
        "total_candidates": len(results),
        "matching_results": results
    }
