.DEFAULT_GOAL := help
PY := .venv/bin/python

.PHONY: help install db test test-cov lint format typecheck security quality check fast fix clean

help:  ## Show available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Install runtime and development dependencies
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m pre_commit install

db:  ## Start PostgreSQL and ensure the test database exists
	scripts/dev-db.sh

# Coverage flags live here rather than in pytest's addopts so that running a
# single test is not measured against a whole-project floor. Every entry
# point that runs the *suite* passes them, so the floor applies wherever the
# suite is invoked from.
test: db  ## Run the whole suite with coverage and the 95% floor
	OTEL_ENABLED=false ENVIRONMENT=test \
	JWT_SECRET=test-only-secret-not-used-outside-tests \
		$(PY) -m pytest --cov=app --cov-report=term-missing

test-cov: db  ## Run the suite and write the HTML coverage report to htmlcov/
	OTEL_ENABLED=false ENVIRONMENT=test \
	JWT_SECRET=test-only-secret-not-used-outside-tests \
		$(PY) -m pytest --cov=app --cov-report=term-missing \
			--cov-report=html

lint:  ## Lint with ruff
	$(PY) -m ruff check .

format:  ## Format with ruff
	$(PY) -m ruff format .

typecheck:  ## Type check with mypy
	$(PY) -m mypy app

security:  ## Security scan the application code
	$(PY) -m bandit -c pyproject.toml -q -r app

## quality is the definition of done: a change is not finished until it passes.
quality:  ## Run the full quality gate (the definition of done)
	scripts/quality.sh

fast:  ## Run static checks only, no tests (edit loop)
	scripts/quality.sh --fast

fix:  ## Apply safe autofixes, then run the full gate
	scripts/quality.sh --fix

# `check` is kept as an alias because existing documentation refers to it.
check: quality  ## Alias for quality

clean:  ## Remove caches and coverage artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
