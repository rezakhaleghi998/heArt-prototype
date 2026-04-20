# heArt Prototype Architecture

The prototype is split into independently deployable frontend and backend services.

- `apps/frontend`: Next.js App Router UI for the public landing page, guided application funnel, media upload, and demo recruiter dashboard.
- `apps/backend`: FastAPI API with SQLAlchemy models, Alembic migrations, repository/service separation, S3-compatible storage abstraction, and Groq screening service.
- `packages/shared`: lightweight contract notes for status enums and future AI tool names.
- `docs`: deployment and architecture notes.

The backend is intentionally structured for AI tool-calling: API schemas are explicit, screening is isolated behind `ScreeningService`, and future RAG/vector search can plug into new services without changing the application funnel routes.

PostgreSQL is required for the MVP schema. `pgvector` is not enabled by default, but a future migration can add an embedding column or side table for candidate/application semantic search.
