.PHONY: help install init test lint format clean run-api run-dashboard run-scheduler docker-build docker-up docker-down

help:
	@echo "Trading Strategy Platform - Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make init             - Initialize database"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linting"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean temporary files"
	@echo "  make run-api          - Run FastAPI server"
	@echo "  make run-dashboard    - Run Streamlit dashboard"
	@echo "  make run-scheduler    - Run task scheduler"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"

install:
	pip install -r requirements.txt
	playwright install chromium

init:
	python scripts/init_db.py

test:
	pytest

lint:
	flake8 src tests
	mypy src

format:
	black src tests scripts
	isort src tests scripts

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov

run-api:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	streamlit run src/dashboard/app.py

run-scheduler:
	python -m src.scheduler.main

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
