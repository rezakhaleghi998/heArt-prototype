import logging

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine
from app.models import application, candidate, consent, media_asset, screening_result  # noqa: F401

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "candidates": {"id", "full_name", "email", "phone", "city"},
    "applications": {"id", "candidate_id", "role", "skills", "portfolio_links", "status", "completion_percent"},
    "media_assets": {"id", "application_id", "kind", "file_name", "content_type", "storage_key", "uploaded"},
    "screening_results": {"id", "application_id", "status", "summary", "fit_score"},
}


def ensure_database_schema() -> None:
    if _has_incompatible_schema():
        from app.core.config import settings

        message = "Existing database schema is incompatible with the heArt MVP schema"
        if not settings.reset_incompatible_schema:
            raise RuntimeError(message)
        logger.warning("%s. Resetting prototype tables.", message)
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema is ready")


def check_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("select 1"))


def _has_incompatible_schema() -> bool:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    for table_name, required_columns in REQUIRED_COLUMNS.items():
        if table_name not in existing_tables:
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        missing_columns = required_columns - existing_columns
        if missing_columns:
            logger.warning("Table %s is missing required columns: %s", table_name, sorted(missing_columns))
            return True
    return False
