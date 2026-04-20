# heArt Candidate Funnel Prototype

Production-minded MVP for an Italian arts and entertainment platform connecting artists, entertainment professionals, cultural companies, and audiences.

The demo shows a conversational application funnel with structured candidate collection, media upload scaffolding, PostgreSQL persistence, Groq-based AI screening, and a recruiter dashboard.

## Folder Structure

```txt
apps/
  backend/      FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Groq, S3-compatible storage
  frontend/     Next.js 14 App Router, TypeScript, Tailwind, React Hook Form, Zod, TanStack Query
packages/
  shared/       API/status contract notes for future tool-calling
docs/
  architecture.md
```

## Local Setup

1. Start PostgreSQL:

```bash
docker compose up -d postgres
```

2. Configure backend:

```bash
cd apps/backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

On Windows PowerShell, activate with:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Configure frontend:

```bash
cd apps/frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Key Environment Variables

Frontend:

- `NEXT_PUBLIC_API_BASE_URL`

Backend:

- `APP_ENV`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `STORAGE_ENDPOINT`
- `STORAGE_ACCESS_KEY`
- `STORAGE_SECRET_KEY`
- `STORAGE_BUCKET`
- `STORAGE_REGION`
- `MAX_UPLOAD_MB`

If `GROQ_API_KEY` is empty, the backend uses a deterministic fallback screening so the demo remains usable.

If storage credentials are empty, upload init returns a local placeholder URL. The frontend still creates and confirms media metadata, which keeps the production API shape intact.

## API Highlights

- `POST /api/v1/applications`
- `PATCH /api/v1/applications/{id}`
- `POST /api/v1/applications/{id}/submit`
- `GET /api/v1/applications`
- `GET /api/v1/applications/{id}`
- `POST /api/v1/uploads/init`
- `POST /api/v1/uploads/confirm`
- `POST /api/v1/applications/{id}/screen`
- `GET /api/v1/health`

## Railway Deploy Steps

1. Create a new Railway project.
2. Add a PostgreSQL service.
3. Add a backend service from this repo:
   - Root directory: `/`
   - Dockerfile path: `apps/backend/Dockerfile`
   - Set `DATABASE_URL` from the Railway PostgreSQL connection string.
   - Set `CORS_ORIGINS` to the deployed frontend URL.
   - Set `GROQ_API_KEY` and `GROQ_MODEL`.
   - Optional: set S3-compatible `STORAGE_*` variables.
4. Deploy the backend. The container runs `alembic upgrade head` before starting Uvicorn.
5. Add a frontend service from this repo:
   - Root directory: `/`
   - Dockerfile path: `apps/frontend/Dockerfile`
   - Set `NEXT_PUBLIC_API_BASE_URL=https://<backend-domain>/api/v1`.
6. Deploy the frontend.
7. Run seed data once from the backend service shell:

```bash
python -m app.seed
```

8. Visit the frontend domain:
   - `/` public landing
   - `/apply` candidate funnel
   - `/admin` demo recruiter dashboard

## Architecture Notes

The backend keeps business logic out of routes:

- repositories handle application persistence and idempotent draft updates
- `StorageService` validates media and creates presigned upload URLs
- `ScreeningService` isolates Groq and fallback parsing
- prompts live in `app/prompts`

The API is shaped so future AI agents can call stable tools: create/update applications, confirm assets, trigger screening, and later run semantic search or casting recommendations.

## Future Improvements

- Add proper recruiter authentication and role-based access.
- Add background jobs for screening and upload virus scanning.
- Add object storage lifecycle policies and signed media previews.
- Add pgvector-backed semantic search for talent discovery.
- Add audit trail tables for GDPR-sensitive operations.
- Add richer tests around submit validation, screening fallback, and upload constraints.
- Add webhooks/events for casting workflow automation.

## Tests

```bash
make test-backend
make test-frontend
```
