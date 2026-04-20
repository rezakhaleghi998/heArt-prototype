.PHONY: backend-dev frontend-dev migrate seed test-backend test-frontend

backend-dev:
	cd apps/backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd apps/frontend && npm run dev

migrate:
	cd apps/backend && alembic upgrade head

seed:
	cd apps/backend && python -m app.seed

test-backend:
	cd apps/backend && pytest

test-frontend:
	cd apps/frontend && npm test
