import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.application import Application, ApplicationAnswer
from app.models.candidate import Candidate
from app.models.consent import Consent
from app.models.enums import ApplicationStatus, AssetKind
from app.models.media_asset import MediaAsset
from app.schemas.application import ApplicationDraftIn


REQUIRED_FIELDS = [
    "candidate.full_name",
    "candidate.email",
    "candidate.city",
    "role",
    "short_bio",
    "years_experience",
    "skills",
    "availability",
]


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def _query(self):
        return (
            select(Application)
            .options(
                selectinload(Application.candidate),
                selectinload(Application.answers),
                selectinload(Application.consents),
                selectinload(Application.media_assets),
                selectinload(Application.screening_result),
            )
            .execution_options(populate_existing=True)
        )

    def list(self, status: ApplicationStatus | None = None) -> list[Application]:
        query = self._query().order_by(Application.created_at.desc())
        if status:
            query = query.where(Application.status == status)
        return list(self.db.scalars(query))

    def get(self, application_id: uuid.UUID) -> Application | None:
        return self.db.scalar(self._query().where(Application.id == application_id))

    def upsert_draft(self, payload: ApplicationDraftIn, application_id: uuid.UUID | None = None) -> Application:
        candidate = self.db.scalar(select(Candidate).where(Candidate.email == payload.candidate.email))
        if candidate is None:
            candidate = Candidate(**payload.candidate.model_dump())
            self.db.add(candidate)
            self.db.flush()
        else:
            for key, value in payload.candidate.model_dump().items():
                setattr(candidate, key, value)

        application = self.get(application_id) if application_id else None
        if application is None:
            application = Application(
                candidate_id=candidate.id,
                role=payload.role,
                short_bio=payload.short_bio,
                years_experience=payload.years_experience,
                skills=payload.skills,
                availability=payload.availability,
                portfolio_links=[str(link) for link in payload.portfolio_links],
                status=ApplicationStatus.draft,
                completion_percent=calculate_completion(payload, []),
            )
            self.db.add(application)
        else:
            application.candidate_id = candidate.id
            application.role = payload.role
            application.short_bio = payload.short_bio
            application.years_experience = payload.years_experience
            application.skills = payload.skills
            application.availability = payload.availability
            application.portfolio_links = [str(link) for link in payload.portfolio_links]
            application.completion_percent = calculate_completion(payload, application.media_assets)
            application.status = ApplicationStatus.draft if application.status == ApplicationStatus.draft else application.status

        self._replace_answers(application, payload)
        self._log_consent(application, payload.gdpr_consent)
        self.db.commit()
        return self.get(application.id) or application

    def submit(self, application: Application) -> Application:
        application.status = ApplicationStatus.submitted
        application.submitted_at = datetime.now(UTC)
        application.completion_percent = max(application.completion_percent, 90)
        self.db.commit()
        return self.get(application.id) or application

    def create_asset(self, application_id: uuid.UUID, kind: AssetKind, file_name: str, content_type: str, size_bytes: int, storage_key: str) -> MediaAsset:
        asset = MediaAsset(
            application_id=application_id,
            kind=kind,
            file_name=file_name,
            content_type=content_type,
            size_bytes=size_bytes,
            storage_key=storage_key,
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def confirm_asset(self, asset_id: uuid.UUID, public_url: str | None = None) -> MediaAsset | None:
        asset = self.db.get(MediaAsset, asset_id)
        if asset is None:
            return None
        asset.uploaded = True
        asset.public_url = public_url
        if asset.application:
            asset.application.completion_percent = max(asset.application.completion_percent, 90)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def _replace_answers(self, application: Application, payload: ApplicationDraftIn) -> None:
        application.answers.clear()
        answer_map = {
            "role": payload.role,
            "short_bio": payload.short_bio or "",
            "years_experience": "" if payload.years_experience is None else str(payload.years_experience),
            "skills": ", ".join(payload.skills),
            "availability": payload.availability or "",
            "portfolio_links": "\n".join([str(link) for link in payload.portfolio_links]),
        }
        for key, value in answer_map.items():
            application.answers.append(ApplicationAnswer(question_key=key, answer_text=value))

    def _log_consent(self, application: Application, accepted: bool) -> None:
        if not accepted:
            return
        has_consent = any(consent.consent_type == "gdpr_application" and consent.accepted for consent in application.consents)
        if not has_consent:
            application.consents.append(Consent(consent_type="gdpr_application", accepted=True))


def calculate_completion(payload: ApplicationDraftIn, media_assets: list[MediaAsset] | None = None) -> int:
    score = 0
    values = {
        "candidate.full_name": payload.candidate.full_name,
        "candidate.email": payload.candidate.email,
        "candidate.city": payload.candidate.city,
        "role": payload.role,
        "short_bio": payload.short_bio,
        "years_experience": payload.years_experience,
        "skills": payload.skills,
        "availability": payload.availability,
    }
    for field in REQUIRED_FIELDS:
        if values.get(field):
            score += 10
    if payload.portfolio_links:
        score += 10
    if payload.gdpr_consent:
        score += 5
    if media_assets and any(asset.kind == AssetKind.intro_video and asset.uploaded for asset in media_assets):
        score += 5
    return min(score, 100)
