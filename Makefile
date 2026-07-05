.PHONY: install dev test lint run worker up down

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src tests

run:
	uvicorn aiplatform.main:app --reload --app-dir src --port 8080

worker:
	celery -A aiplatform.workers.celery_app:celery_app worker --loglevel=INFO

up:
	docker compose up --build

down:
	docker compose down -v
