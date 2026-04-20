import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import ApplicationStatus
from app.repositories.applications import ApplicationRepository
from app.schemas.application import (
    ApplicationDraftIn,
    ApplicationListOut,
    ApplicationOut,
    ApplicationUpdateIn,
    ConfirmAssetIn,
    MediaAssetOut,
    ScreeningOut,
    UploadInitIn,
    UploadInitOut,
)
from app.services.screening import ScreeningService
from app.services.storage import StorageService

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "heart-backend"}


@router.post("/applications", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationDraftIn, db: Session = Depends(get_db)) -> ApplicationOut:
    return ApplicationRepository(db).upsert_draft(payload)


@router.patch("/applications/{application_id}", response_model=ApplicationOut)
def update_application(application_id: uuid.UUID, payload: ApplicationUpdateIn, db: Session = Depends(get_db)) -> ApplicationOut:
    repo = ApplicationRepository(db)
    if repo.get(application_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return repo.upsert_draft(payload, application_id=application_id)


@router.post("/applications/{application_id}/submit", response_model=ApplicationOut)
def submit_application(application_id: uuid.UUID, db: Session = Depends(get_db)) -> ApplicationOut:
    repo = ApplicationRepository(db)
    application = repo.get(application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    has_video = any(asset.kind == "intro_video" and asset.uploaded for asset in application.media_assets)
    if not has_video:
        # Draft mode remains possible because the frontend can save before calling submit.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Intro video richiesto per inviare la candidatura")
    submitted = repo.submit(application)
    ScreeningService(db).screen(submitted)
    return repo.get(application_id) or submitted


@router.get("/applications/{application_id}", response_model=ApplicationOut)
def get_application(application_id: uuid.UUID, db: Session = Depends(get_db)) -> ApplicationOut:
    application = ApplicationRepository(db).get(application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.get("/applications", response_model=ApplicationListOut)
def list_applications(
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> ApplicationListOut:
    items = ApplicationRepository(db).list(status_filter)
    return ApplicationListOut(items=items, total=len(items))


@router.post("/uploads/init", response_model=UploadInitOut)
def init_upload(payload: UploadInitIn, db: Session = Depends(get_db)) -> UploadInitOut:
    repo = ApplicationRepository(db)
    application = repo.get(payload.application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    storage = StorageService()
    storage.validate_upload(payload.kind, payload.content_type, payload.size_bytes)
    key = storage.build_key(payload.application_id, payload.file_name)
    asset = repo.create_asset(payload.application_id, payload.kind, payload.file_name, payload.content_type, payload.size_bytes, key)
    return UploadInitOut(asset_id=asset.id, upload_url=storage.presigned_put_url(key, payload.content_type), storage_key=key)


@router.post("/uploads/confirm", response_model=MediaAssetOut)
def confirm_upload(payload: ConfirmAssetIn, db: Session = Depends(get_db)) -> MediaAssetOut:
    asset = ApplicationRepository(db).confirm_asset(payload.asset_id, payload.public_url)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.post("/applications/{application_id}/screen", response_model=ScreeningOut)
def trigger_screening(application_id: uuid.UUID, db: Session = Depends(get_db)) -> ScreeningOut:
    application = ApplicationRepository(db).get(application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return ScreeningService(db).screen(application)
