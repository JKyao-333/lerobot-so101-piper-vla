.PHONY: install-dev test lint validate workflow-dry-run reference-profile check-secrets check-large-files

PYTHON ?= python

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m compileall -q src scripts
	$(PYTHON) -m ruff check src scripts tests

validate:
	bash scripts/validate_repository.sh

workflow-dry-run:
	bash scripts/validate_workflow_previews.sh

reference-profile:
	$(PYTHON) scripts/validate_reference_profile.py --json

check-secrets:
	$(PYTHON) scripts/sanitize_logs.py --check-repository .

check-large-files:
	$(PYTHON) scripts/check_repository_files.py --root . --max-mb 20
