import json
import logging
import uuid

import httpx
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.models.application import Application
from app.models.enums import ApplicationStatus, ScreeningStatus
from app.models.screening_result import ScreeningResult
from app.prompts.screening import SCREENING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ScreeningPayload(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    fit_score: int = Field(ge=1, le=10)
    recommended_next_action: str


class ScreeningService:
    def __init__(self, db: Session):
        self.db = db

    def screen(self, application: Application) -> ScreeningResult:
        result = application.screening_result or ScreeningResult(application_id=application.id, status=ScreeningStatus.pending)
        self.db.add(result)
        application.status = ApplicationStatus.screening
        self.db.commit()

        try:
            payload = self._screen_with_groq(application) if settings.groq_api_key else self._fallback_screening(application)
            result.status = ScreeningStatus.completed
            result.summary = payload.summary
            result.strengths = payload.strengths
            result.risks = payload.risks
            result.fit_score = payload.fit_score
            result.recommended_next_action = payload.recommended_next_action
            result.raw_response = payload.model_dump()
            application.status = ApplicationStatus.reviewed
        except Exception as exc:
            logger.exception("AI screening failed for application %s", application.id)
            result.status = ScreeningStatus.failed
            result.summary = "Screening automatico non disponibile. Revisione manuale consigliata."
            result.risks = [str(exc)[:240]]
            result.fit_score = None
            result.recommended_next_action = "Revisione manuale"
            application.status = ApplicationStatus.submitted

        self.db.commit()
        self.db.refresh(result)
        return result

    @retry(wait=wait_exponential(multiplier=1, min=1, max=6), stop=stop_after_attempt(2))
    def _screen_with_groq(self, application: Application) -> ScreeningPayload:
        body = {
            "model": settings.groq_model,
            "messages": [
                {"role": "system", "content": SCREENING_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(self._application_context(application), ensure_ascii=False)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"},
                json=body,
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return self._parse_json(content)

    def _parse_json(self, content: str) -> ScreeningPayload:
        try:
            return ScreeningPayload.model_validate_json(content)
        except ValidationError:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return ScreeningPayload.model_validate(json.loads(content[start:end]))
            raise

    def _fallback_screening(self, application: Application) -> ScreeningPayload:
        missing = []
        if not application.short_bio:
            missing.append("bio breve mancante")
        if not application.portfolio_links:
            missing.append("portfolio non presente")
        if not any(asset.uploaded for asset in application.media_assets):
            missing.append("intro video non confermato")
        score = 8 if application.years_experience and application.years_experience >= 5 else 6
        if missing:
            score = max(4, score - 2)
        return ScreeningPayload(
            summary=f"{application.candidate.full_name} si candida come {application.role} con competenze in {', '.join(application.skills[:4]) or 'area artistica'}." ,
            strengths=application.skills[:4] or ["Profilo strutturato raccolto tramite funnel conversazionale"],
            risks=missing or ["Nessun rischio evidente nel set dati MVP"],
            fit_score=score,
            recommended_next_action="Invitare a colloquio conoscitivo" if score >= 7 else "Richiedere integrazione materiali",
        )

    def _application_context(self, application: Application) -> dict:
        return {
            "application_id": str(application.id),
            "candidate": {
                "name": application.candidate.full_name,
                "city": application.candidate.city,
            },
            "role": application.role,
            "short_bio": application.short_bio,
            "years_experience": application.years_experience,
            "skills": application.skills,
            "availability": application.availability,
            "portfolio_links": application.portfolio_links,
            "media_assets": [
                {"kind": asset.kind, "content_type": asset.content_type, "uploaded": asset.uploaded}
                for asset in application.media_assets
            ],
        }
