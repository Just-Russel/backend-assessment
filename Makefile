SHELL=/bin/bash
.SHELLFLAGS=-ce
.ONESHELL:

# Don't use dashes in the service name
SERVICE_NAME ?= api_template
DB_USER ?= api_template_db_user
DB_PASSWORD ?= api_template_db_user

TAG ?= latest
CONTAINER=$(SERVICE_NAME):$(TAG)
export PORT ?= 80
DB_SUPERUSER ?= justrussel
DB_SUPERUSER_PASSWORD ?= justrussel
DB_HOST ?= localhost
DB_NAME ?= $(SERVICE_NAME)
DB_PORT ?= 5432

help:
	@echo "Use 'make setup' to install the necessary dependencies."
	@echo "The following targets may be useful:"
	@echo "- lint: Lint the code."
	@echo "- format: Format the code."
	@echo "- debug: Run the code without containers."
	@echo "- test: Run all tests in the codebase."
	@echo "- cov: Run all tests and generate a coverage report."
	@echo "- build: Build a production-grade container."
	@echo "- run: Run the code in a production-grade container."
	@echo "- publish: Build and push a production-grade container."

uv:
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

setup: uv
	uv sync

dev-setup: uv
	uv sync --dev

lint: uv dev-setup type-check
	uv run ruff check

format: uv dev-setup
	uv run ruff check --select I --fix
	uv run ruff format

type-check: uv dev-setup
	uv run mypy src/

test: uv dev-setup
	uv run pytest src/ tests/ -v

unit-tests: uv dev-setup
	uv run pytest src/ -m 'not system'

integration-tests: uv dev-setup
	uv run pytest tests/

cov: uv dev-setup
	uv run pytest -v -m 'not system' --cov=src/ --cov-report=xml

debug: uv dev-setup
	uv run python -m src

build: lint test
	docker buildx build --load -t $(CONTAINER) .

publish: build
	docker push $(CONTAINER)

run: build
	docker run --network=host -e PORT=$(PORT) $(CONTAINER)

init-db:
	# Kill any connections to the database
	PGPASSWORD=$(DB_SUPERUSER_PASSWORD) psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_SUPERUSER) --dbname postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = '$(DB_NAME)';";

	# Create the service user.
	# Drop and recreate the database
	PGPASSWORD=$(DB_SUPERUSER_PASSWORD) psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_SUPERUSER) --dbname postgres -c "DROP DATABASE IF EXISTS $(DB_NAME);"
	PGPASSWORD=$(DB_SUPERUSER_PASSWORD) psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_SUPERUSER) --dbname postgres -c "DROP USER IF EXISTS $(DB_USER);"
	PGPASSWORD=$(DB_SUPERUSER_PASSWORD) psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_SUPERUSER) --dbname postgres -c "CREATE USER $(DB_USER) WITH PASSWORD '$(DB_PASSWORD)' CREATEDB" || true
	PGPASSWORD=$(DB_SUPERUSER_PASSWORD) psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_SUPERUSER) --dbname postgres -c "CREATE DATABASE $(DB_NAME) OWNER $(DB_USER);"
.PHONY: init-db

generate-migrations:
	uv run alembic revision --autogenerate -m "$(MESSAGE)"

check-migrations:
	uv run alembic check

apply-migrations:
	uv run alembic upgrade head

secrets:
	mkdir secrets || true
	uv run gcloud secrets versions access latest --secret=$(FIREBASE_SERVICE_ACCOUNT_SECRET) > $(FIREBASE_CREDENTIALS_PATH)
	chmod 740 $(FIREBASE_CREDENTIALS_PATH)
.PHONY: secrets

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache .ruff_cache .coverage .htmlcov
