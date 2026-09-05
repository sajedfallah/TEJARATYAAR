.PHONY: up down test migrate seed

up:
	docker compose up -d

down:
	docker compose down

test:
	cd backend && pip install -r requirements.txt && pytest -q

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python scripts/seed_access_control.py
