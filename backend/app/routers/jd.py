
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.jd_parser import analyze_job_description


router = APIRouter(
    prefix="/job-description",
    tags=["Job Description"]
)


class JobDescriptionRequest(BaseModel):
    jd_text: str


@router.post("/analyze")
def analyze_jd(request: JobDescriptionRequest):

    try:
        result = analyze_job_description(request.jd_text)

        return {
            "message": "Job description analyzed successfully",
            "job_requirements": result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
