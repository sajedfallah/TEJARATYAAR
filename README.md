# TEJARATYAAR

> Telegram-first Customs Operations CRM for customs clearance companies.

## Status

**V1 Foundation — active development**

The repository is the single source of truth for product decisions, architecture, implementation, tests, and release history.

## Product scope

- Case / Pre-Case management
- Customer and contact management
- Customs and case-type configuration
- Tasks, activities, milestones and commitments
- Document center and customer document requests
- Customer requests and customer-facing updates
- Internal Case Room and notifications
- Role-based access control and case-level isolation
- Manager / Supervisor / Employee / Customer workspaces
- Audit trail, reporting, CSAT and exports
- Telegram Bot + Telegram Mini App

## Architecture

```text
Telegram Bot / Mini App
          |
       FastAPI
          |
   Modular Business Layer
      /          \
PostgreSQL      Redis/Worker
          |
     Object Storage
```

V1 intentionally uses a **modular monolith**. This keeps the first release maintainable while leaving clear boundaries for future extraction of services.

## Repository layout

```text
backend/      FastAPI, domain logic, database and API
frontend/     React + TypeScript Telegram Mini App
bot/          Telegram bot runtime
worker/       Background jobs
migrations/  Database migration history
scripts/      Developer/operations scripts
docs/         Product, architecture and delivery documentation
.github/      CI and repository automation
tests/        Cross-module / E2E tests
```

## Local development

### Infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL and Redis for local development.

### API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check: `GET /health`

### Tests

```bash
make api-test
```

## Engineering rules

1. Business rules live on the server, never only in the UI.
2. Customer data is isolated by server-side authorization.
3. Important state changes are auditable.
4. Case is the operational center of the product.
5. No secrets are committed; `.env.example` contains placeholders only.
6. Every feature requires validation, authorization and tests before release.
7. Existing case/workflow history must not be broken by template changes.

## Documentation

- `PROJECT_HANDOVER.md` — project continuity and audit baseline
- `docs/PRODUCT_SPECIFICATION.md` — product requirements
- `docs/ARCHITECTURE.md` — technical architecture
- `docs/DATABASE_DESIGN.md` — data model direction
- `docs/DEVELOPMENT_RULES.md` — engineering standards
- `docs/ROADMAP.md` — delivery plan

## License

License policy will be finalized before the first public production release.
