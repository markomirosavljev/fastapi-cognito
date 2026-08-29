.DEFAULT_GOAL := help

.PHONY: help install lock test test-down build publish clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies (including test group) via uv
	uv sync --group test

lock:
	uv lock

test: ## Run the test suite in Docker
	docker compose -f docker-compose-tests.yaml up --build --exit-code-from fastapi_cognito_tests --abort-on-container-exit

test-down: ## Tear down and remove test containers/volumes
	docker compose -f docker-compose-tests.yaml down --volumes --remove-orphans

build:
	uv build

publish: build
	uv publish

clean: ## Remove build artifacts and caches
	rm -rf dist build *.egg-info
	find . -type d -name '__pycache__' -not -path './.git/*' -exec rm -rf {} +
