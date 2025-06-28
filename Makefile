start:
	uv run backend/src/main.py

dc-restart-backend:
	docker compose build backend
	docker compose up -d
	docker logs --follow backend-fastapi-base-cnt
