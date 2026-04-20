import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ScreeningStatus


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), unique=True, index=True)
    status: Mapped[ScreeningStatus] = mapped_column(Enum(ScreeningStatus), default=ScreeningStatus.pending, index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    strengths: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    fit_score: Mapped[int | None] = mapped_column(Integer)
    recommended_next_action: Mapped[str | None] = mapped_column(String(255))
    raw_response: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    application = relationship("Application", back_populates="screening_result")
