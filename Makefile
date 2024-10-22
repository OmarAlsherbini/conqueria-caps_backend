# Makefile for Conqueria Caps project

# Variables
DOCKER_COMPOSE_TEST = docker-compose -f docker-compose.test.yml
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.prod.yml
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.dev.yml
RUN_TESTS_SCRIPT = ./run_tests.sh

.PHONY: test up-test down-test logs-test
.PHONY: prod up-prod down-prod logs-prod
.PHONY: dev up-dev down-dev logs-dev
.PHONY: run-tests

# Test Environment
test: up-test
up-test:
	$(DOCKER_COMPOSE_TEST) build --no-cache --build-arg ENVIRONMENT=test
	$(DOCKER_COMPOSE_TEST) up -d

up-log-test:
	clear && $(DOCKER_COMPOSE_TEST) build --no-cache --build-arg ENVIRONMENT=test
	$(DOCKER_COMPOSE_TEST) up -d && docker compose -f docker-compose.test.yml logs -f web-test

down-test:
	$(DOCKER_COMPOSE_TEST) down

log-test:
	$(DOCKER_COMPOSE_TEST) logs -f --tail 200

empty-test:
	$(DOCKER_COMPOSE_TEST) build --no-cache --build-arg ENVIRONMENT=test
	$(DOCKER_COMPOSE_TEST) up -d
	
	# Set environment variables and ensure they're available for the next commands
	# Run the database command within docker-compose
	set -a; \
	. ./.env.test; \
	set +a; \
	echo "Emptying the database for User: $$POSTGRES_USER, Database: $$POSTGRES_DB"
	docker-compose -f docker-compose.test.yml exec db-test bash -c '/usr/local/bin/empty_db.sh $$POSTGRES_USER $$POSTGRES_DB'

	echo "Deleting all test migrations..."
	rm -rf migrations/test_versions/*

	echo "Test environment cleaned up successfully."
	$(DOCKER_COMPOSE_TEST) down

# Production Environment
prod: up-prod
up-prod:
	$(DOCKER_COMPOSE_PROD) build --no-cache --build-arg ENVIRONMENT=prod
	$(DOCKER_COMPOSE_PROD) up -d

up-log-prod:
	clear && $(DOCKER_COMPOSE_PROD) build --no-cache --build-arg ENVIRONMENT=prod
	$(DOCKER_COMPOSE_PROD) up -d

down-prod:
	$(DOCKER_COMPOSE_PROD) down

log-prod:
	$(DOCKER_COMPOSE_PROD) logs -f --tail 200

empty-prod:
	$(DOCKER_COMPOSE_PROD) build --no-cache --build-arg ENVIRONMENT=prod
	$(DOCKER_COMPOSE_PROD) up -d
	
	# Set environment variables and ensure they're available for the next commands
	# Run the database command within docker-compose
	set -a; \
	. ./.env.prod; \
	set +a; \
	echo "Emptying the database for User: $$POSTGRES_USER, Database: $$POSTGRES_DB"
	docker-compose -f docker-compose.prod.yml exec db-prod bash -c '/usr/local/bin/empty_db.sh $$POSTGRES_USER $$POSTGRES_DB'

	echo "Deleting all production migrations..."
	rm -rf migrations/prod_versions/*

	echo "Prod environment cleaned up successfully."
	$(DOCKER_COMPOSE_PROD) down

# Development Environment
dev: up-dev
up-dev:
	$(DOCKER_COMPOSE_DEV) build --no-cache --build-arg ENVIRONMENT=dev
	$(DOCKER_COMPOSE_DEV) up -d

up-dev-no-docker:
	ENVIRONMENT=db_only alembic upgrade head
	ENVIRONMENT=db_only uvicorn app.main:app --port 8004 --reload

up-dev-no-docker-alembic:
	pip install -r requirements.txt
	ENVIRONMENT=db_only alembic revision --autogenerate -m "Auto-Generated in local device" --version-path "migrations/db_only_versions"
	ENVIRONMENT=db_only alembic upgrade head
	ENVIRONMENT=db_only uvicorn app.main:app --port 8004 --reload

up-log-dev:
	clear && $(DOCKER_COMPOSE_DEV) build --no-cache --build-arg ENVIRONMENT=dev
	$(DOCKER_COMPOSE_DEV) up -d && docker compose -f docker-compose.dev.yml logs -f web-dev

down-dev:
	$(DOCKER_COMPOSE_DEV) down

log-dev:
	$(DOCKER_COMPOSE_DEV) logs -f --tail 200

empty-dev:
	$(DOCKER_COMPOSE_DEV) build --no-cache --build-arg ENVIRONMENT=dev
	$(DOCKER_COMPOSE_DEV) up -d

	@echo "Emptying the development database by dropping all tables..."


	# Set environment variables and ensure they're available for the next commands
	# Run the database command within docker-compose
	set -a; \
	. ./.env.dev; \
	set +a; \
	echo "Emptying the database for User: $$POSTGRES_USER, Database: $$POSTGRES_DB"
	docker-compose -f docker-compose.dev.yml exec db-dev bash -c '/usr/local/bin/empty_db.sh $$POSTGRES_USER $$POSTGRES_DB'

	@echo "Deleting all development migrations..."
	rm -rf migrations/dev_versions/*

	@echo "Dev environment cleaned up successfully."


	$(DOCKER_COMPOSE_DEV) down

# Run tests
run-tests:
	clear && $(RUN_TESTS_SCRIPT)

# Helper target to run all tests and bring the test environment down afterward
test-all: test run-tests down-test
