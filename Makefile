.DEFAULT_GOAL := help

.PHONY: help install lock test test-down build publish publish-dry clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies (including test group) via Poetry
	poetry install --no-interaction --no-ansi --with test

lock:
	poetry lock --no-update

test: ## Run the test suite in Docker
	docker compose -f docker-compose-tests.yaml up --build --exit-code-from fastapi_cognito_tests --abort-on-container-exit

test-down: ## Tear down and remove test containers/volumes
	docker compose -f docker-compose-tests.yaml down --volumes --remove-orphans

build:
	poetry build

publish: build
	poetry publish

publish-dry: build
	poetry publish --dry-run

clean: ## Remove build artifacts and caches
	rm -rf dist build *.egg-info
	find . -type d -name '__pycache__' -not -path './.git/*' -exec rm -rf {} +
