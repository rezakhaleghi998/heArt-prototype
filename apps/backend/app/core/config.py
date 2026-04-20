from functools import lru_cache

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/heart"
    cors_origins: str = "http://localhost:3000"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    storage_endpoint: str | None = None
    storage_access_key: str | None = None
    storage_secret_key: str | None = None
    storage_bucket: str = "heart-demo"
    storage_region: str = "eu-south-1"
    max_upload_mb: int = Field(default=250, ge=1, le=2048)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def model_post_init(self, __context: object) -> None:
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
