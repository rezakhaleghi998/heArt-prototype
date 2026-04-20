import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(160), index=True)
    short_bio: Mapped[str | None] = mapped_column(Text)
    years_experience: Mapped[int | None] = mapped_column(Integer)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    availability: Mapped[str | None] = mapped_column(String(160))
    portfolio_links: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.draft, index=True)
    completion_percent: Mapped[int] = mapped_column(Integer, default=0)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    candidate = relationship("Candidate", back_populates="applications")
    answers = relationship("ApplicationAnswer", back_populates="application", cascade="all, delete-orphan")
    media_assets = relationship("MediaAsset", back_populates="application", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="application", cascade="all, delete-orphan")
    screening_result = relationship("ScreeningResult", back_populates="application", cascade="all, delete-orphan", uselist=False)


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    question_key: Mapped[str] = mapped_column(String(80), index=True)
    answer_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="answers")
