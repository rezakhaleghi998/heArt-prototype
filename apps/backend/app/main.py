import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.logging import request_logging_middleware

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="heArt Candidate Funnel API",
    version="0.1.0",
    description="Production-minded MVP API for conversational artist applications.",
)

app.middleware("http")(request_logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "heArt API", "docs": "/docs"}
