# -------- Commands --------
UV := uv
PKG := app

.PHONY: help sync dev lint fmt typecheck test cov hooks clean run-once scheduler migrate revision

help:
	@echo "Targets:"
	@echo "  sync        - install prod deps (uv sync)"
	@echo "  dev         - install prod+dev deps (uv sync --all-groups)"
	@echo "  lint        - ruff check --fix"
	@echo "  fmt         - ruff format"
	@echo "  typecheck   - mypy"
	@echo "  test        - pytest"
	@echo "  cov         - coverage run + report"
	@echo "  hooks       - install pre-commit hooks"
	@echo "  run-once    - python -m app.main run-once"
	@echo "  scheduler   - python -m app.main run-scheduler --hours 3"
	@echo "  migrate     - alembic upgrade head"
	@echo "  revision    - alembic revision -m 'msg'"
	@echo "  clean       - remove caches"

sync:
	$(UV) sync

dev:
	$(UV) sync --all-groups

lint:
	$(UV) run ruff check --fix

fmt:
	$(UV) run ruff format

typecheck:
	$(UV) run mypy $(PKG)

test:
	PYTHONPATH=. $(UV) run pytest -q

cov:
	PYTHONPATH=. $(UV) run coverage run -m pytest && $(UV) run coverage report -m

hooks:
	$(UV) run pre-commit install

run-once:
	PYTHONPATH=. $(UV) run python -m app.main run-once

scheduler:
	PYTHONPATH=. $(UV) run python -m app.main run-scheduler --hours 3 --jitter 30

migrate:
	$(UV) run alembic upgrade head

revision:
	@if [ -z "$(m)" ]; then echo "Usage: make revision m='message'"; exit 1; fi
	$(UV) run alembic revision -m "$(m)"

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage
