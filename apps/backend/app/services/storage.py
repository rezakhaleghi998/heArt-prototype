import mimetypes
import uuid

import boto3
from botocore.client import Config
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.enums import AssetKind


ALLOWED_CONTENT_TYPES = {
    AssetKind.profile_image: {"image/jpeg", "image/png", "image/webp"},
    AssetKind.intro_video: {"video/mp4", "video/quicktime", "video/webm"},
    AssetKind.portfolio: {"application/pdf", "image/jpeg", "image/png"},
}


class StorageService:
    def validate_upload(self, kind: AssetKind, content_type: str, size_bytes: int) -> None:
        allowed = ALLOWED_CONTENT_TYPES[kind]
        if content_type not in allowed:
            guessed = mimetypes.guess_extension(content_type) or content_type
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo file non supportato: {guessed}")
        if size_bytes > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File troppo grande per questo prototipo")

    def build_key(self, application_id: uuid.UUID, file_name: str) -> str:
        safe_name = file_name.replace("/", "-").replace("\\", "-")
        return f"applications/{application_id}/{uuid.uuid4()}-{safe_name}"

    def presigned_put_url(self, storage_key: str, content_type: str) -> str:
        if not settings.storage_access_key or not settings.storage_secret_key:
            return f"https://storage.local/{settings.storage_bucket}/{storage_key}"
        client = boto3.client(
            "s3",
            endpoint_url=settings.storage_endpoint,
            aws_access_key_id=settings.storage_access_key,
            aws_secret_access_key=settings.storage_secret_key,
            region_name=settings.storage_region,
            config=Config(signature_version="s3v4"),
        )
        return client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.storage_bucket, "Key": storage_key, "ContentType": content_type},
            ExpiresIn=900,
        )
