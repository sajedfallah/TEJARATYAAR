.PHONY: up down api-test

up:
	docker compose up -d

down:
	docker compose down

api-test:
	cd backend && pip install -r requirements.txt && pip install pytest httpx && pytest -q
