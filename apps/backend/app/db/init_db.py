import logging

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.models import application, candidate, consent, media_asset, screening_result  # noqa: F401

logger = logging.getLogger(__name__)


def ensure_database_schema() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema is ready")


def check_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("select 1"))
