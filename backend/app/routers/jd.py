
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.jd_parser import analyze_job_description
from app.database import get_db
from app.models import JobDescription


router = APIRouter(
    prefix="/job-description",
    tags=["Job Description"]
)


class JobDescriptionRequest(BaseModel):
    jd_text: str
    title: str | None = None


# Analyze and save a job description
@router.post("/analyze")
def analyze_jd(
    request: JobDescriptionRequest,
    db: Session = Depends(get_db)
):

    try:
        result = analyze_job_description(request.jd_text)

        new_jd = JobDescription(
            title=request.title,
            jd_text=request.jd_text,
            requirements=result
        )

        db.add(new_jd)
        db.commit()
        db.refresh(new_jd)

        return {
            "message": "Job description analyzed and saved successfully",
            "job_description_id": new_jd.id,
            "job_requirements": result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze or save job description"
        )


# Get all saved job descriptions
@router.get("/")
def get_all_job_descriptions(
    db: Session = Depends(get_db)
):

    job_descriptions = (
        db.query(JobDescription)
        .order_by(JobDescription.id.desc())
        .all()
    )

    return {
        "total": len(job_descriptions),
        "job_descriptions": [
            {
                "id": jd.id,
                "title": jd.title,
                "jd_text": jd.jd_text,
                "requirements": jd.requirements,
                "created_at": jd.created_at
            }
            for jd in job_descriptions
        ]
    }


# Get a specific job description by ID
@router.get("/{jd_id}")
def get_job_description(
    jd_id: int,
    db: Session = Depends(get_db)
):

    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id
    ).first()

    if jd is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    return {
        "id": jd.id,
        "title": jd.title,
        "jd_text": jd.jd_text,
        "requirements": jd.requirements,
        "created_at": jd.created_at
    }


# Delete a job description by ID
@router.delete("/{jd_id}")
def delete_job_description(
    jd_id: int,
    db: Session = Depends(get_db)
):

    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id
    ).first()

    if jd is None:
        raise HTTPException(
            status_code=404,
            detail="Job description not found"
        )

    db.delete(jd)
    db.commit()

    return {
        "message": "Job description deleted successfully",
        "deleted_id": jd_id
    }
