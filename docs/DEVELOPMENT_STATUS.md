# Development Status

## Current release line

V1 Foundation

## Completed

- Repository established as the canonical project source.
- Product specification and architecture documentation recorded.
- FastAPI backend entrypoint created.
- Typed backend configuration added.
- SQLAlchemy database foundation added.
- Alembic configuration added.
- Local PostgreSQL and Redis development infrastructure added.
- React + TypeScript RTL Mini App shell created.
- Telegram bot and background-worker entrypoints reserved.
- Backend health endpoint and automated test added.
- GitHub Actions CI added for the backend test suite.
- Environment template and secret-safe gitignore added.

## In progress

1. Domain models and database schema.
2. Alembic initial migration.
3. Authentication and Telegram identity binding.
4. RBAC and server-side permission engine.
5. Customer isolation.

## Not yet production-ready

The current code is a foundation only. Authentication, authorization, persistent domain models, Telegram integration, document storage, workflows and production deployment controls must be implemented and tested before deployment.

## Release gate

No production release until the end-to-end scenario in the product specification passes, security checks pass, migrations are reproducible, backups are tested, and CI is green.
