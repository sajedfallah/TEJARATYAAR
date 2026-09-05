# Development Status

## Current release line

V1 Foundation — Identity & Access Core

## Completed

- Repository established as the canonical project source.
- Product specification and architecture documentation recorded.
- FastAPI backend entrypoint created.
- Typed backend configuration added.
- SQLAlchemy database foundation added.
- Alembic runtime configuration added.
- Initial identity/CRM migration added.
- Core models added for users, roles, permissions, teams, customers, contacts, invites and audit logs.
- Telegram Mini App init-data signature verification added.
- JWT access-token creation/validation added.
- Server-side RBAC permission dependency added.
- Telegram login and `/api/v1/auth/me` endpoints added.
- System RBAC bootstrap definitions and seed command added.
- Local PostgreSQL and Redis development infrastructure added.
- React + TypeScript RTL Mini App shell created.
- Telegram bot and background-worker entrypoints reserved.
- Backend health endpoint and automated tests added.
- GitHub Actions CI added for the backend test suite.
- Environment template and secret-safe gitignore added.

## In progress / next

1. Invite issuance and one-time activation workflow.
2. Customer-contact Telegram binding and customer isolation policy.
3. CRUD APIs for users, teams, customers and contacts.
4. Customs-office and Case Type models.
5. Pre-Case and Case domain engine.
6. Integration tests against PostgreSQL migrations.

## Security gates

- Production must use a high-entropy `JWT_SECRET`; the development default is forbidden in production.
- Telegram authentication must always validate signed Mini App `initData` server-side.
- Customer-visible APIs must enforce customer/contact scope in the backend, never only in the frontend.
- All privileged mutations must be permission-checked and audited.

## Not yet production-ready

The repository now contains a real identity and access-control foundation, but V1 is not deployable for business use yet. Invite activation, customer isolation, Case permissions, persistent operational domains, file security, backups, production configuration and end-to-end tests remain required.

## Release gate

No production release until the end-to-end scenario in the product specification passes, security checks pass, migrations are reproducible on an empty PostgreSQL database, backups are tested, and CI is green.
