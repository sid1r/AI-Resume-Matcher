
"""Recruiter registration, login and authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.auth_models import Recruiter
from app.auth.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    RecruiterResponse,
    TokenResponse,
)
from app.auth.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer(auto_error=False)


@router.post(
    "/register",
    response_model=RecruiterResponse,
    status_code=status.HTTP_201_CREATED
)
def register_recruiter(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = data.email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address."
        )

    existing_recruiter = db.query(Recruiter).filter(
        Recruiter.email == email
    ).first()

    if existing_recruiter:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered."
        )

    recruiter = Recruiter(
        name=data.name.strip(),
        email=email,
        hashed_password=hash_password(data.password)
    )

    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)

    return recruiter


@router.post("/login", response_model=TokenResponse)
def login_recruiter(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = data.email.strip().lower()

    recruiter = db.query(Recruiter).filter(
        Recruiter.email == email
    ).first()

    if not recruiter or not verify_password(
        data.password,
        recruiter.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(recruiter.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_current_recruiter(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    recruiter_id = decode_access_token(credentials.credentials)

    if recruiter_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

    recruiter = db.query(Recruiter).filter(
        Recruiter.id == recruiter_id
    ).first()

    if recruiter is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Recruiter account not found."
        )

    return recruiter


@router.get("/me", response_model=RecruiterResponse)
def get_my_account(
    current_recruiter: Recruiter = Depends(get_current_recruiter)
):
    return current_recruiter
