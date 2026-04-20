import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import router
from app.core.config import settings
from app.core.logging import request_logging_middleware
from app.db.init_db import ensure_database_schema

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


@app.on_event("startup")
def startup() -> None:
    ensure_database_schema()


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logging.exception("Database error on %s", request.url.path)
    detail = str(getattr(exc, "orig", exc)) if settings.debug_errors else "Database error"
    return JSONResponse(status_code=500, content={"detail": detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.exception("Unhandled error on %s", request.url.path)
    detail = str(exc) if settings.debug_errors else "Internal server error"
    return JSONResponse(status_code=500, content={"detail": detail})


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "heArt API", "docs": "/docs"}
