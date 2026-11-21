
"""SQLAlchemy database models."""

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    jd_text: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    requirements: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    matching_results: Mapped[list["MatchingResult"]] = relationship(
        back_populates="job_description"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    resume_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    candidate_information: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    matching_results: Mapped[list["MatchingResult"]] = relationship(
        back_populates="candidate"
    )


class MatchingResult(Base):
    __tablename__ = "matching_results"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False
    )

    job_description_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False
    )

    overall_matching_score: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    rank: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    matching_analysis: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    candidate: Mapped["Candidate"] = relationship(
        back_populates="matching_results"
    )

    job_description: Mapped["JobDescription"] = relationship(
        back_populates="matching_results"
    )
