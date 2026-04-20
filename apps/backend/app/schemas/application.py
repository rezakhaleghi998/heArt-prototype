import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from app.models.enums import ApplicationStatus, AssetKind, ScreeningStatus


class CandidateIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=180)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=80)
    city: str | None = Field(default=None, max_length=160)


class ApplicationDraftIn(BaseModel):
    candidate: CandidateIn
    role: str = Field(min_length=2, max_length=160)
    short_bio: str | None = Field(default=None, max_length=2000)
    years_experience: int | None = Field(default=None, ge=0, le=80)
    skills: list[str] = Field(default_factory=list, max_length=30)
    availability: str | None = Field(default=None, max_length=160)
    portfolio_links: list[str] = Field(default_factory=list, max_length=10)
    gdpr_consent: bool = False

    @field_validator("skills")
    @classmethod
    def clean_skills(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ApplicationUpdateIn(ApplicationDraftIn):
    pass


class UploadInitIn(BaseModel):
    application_id: uuid.UUID
    kind: AssetKind
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=3, max_length=120)
    size_bytes: int = Field(gt=0)


class UploadInitOut(BaseModel):
    asset_id: uuid.UUID
    upload_url: str
    storage_key: str
    headers: dict[str, str] = Field(default_factory=dict)


class ConfirmAssetIn(BaseModel):
    asset_id: uuid.UUID
    public_url: str | None = None


class MediaAssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: AssetKind
    file_name: str
    content_type: str
    size_bytes: int
    storage_key: str
    public_url: str | None
    uploaded: bool


class ScreeningOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: ScreeningStatus
    summary: str | None
    strengths: list[str]
    risks: list[str]
    fit_score: int | None
    recommended_next_action: str | None


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    phone: str | None
    city: str | None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate: CandidateOut
    role: str
    short_bio: str | None
    years_experience: int | None
    skills: list[str]
    availability: str | None
    portfolio_links: list[str]
    status: ApplicationStatus
    completion_percent: int
    submitted_at: datetime | None
    media_assets: list[MediaAssetOut] = Field(default_factory=list)
    screening_result: ScreeningOut | None = None
    created_at: datetime
    updated_at: datetime


class ApplicationListOut(BaseModel):
    items: list[ApplicationOut]
    total: int
