.PHONY: install-dev test lint validate workflow-dry-run experiment-baseline check-secrets check-large-files

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

experiment-baseline:
	$(PYTHON) scripts/validate_experiment_baseline.py --json

check-secrets:
	$(PYTHON) scripts/sanitize_logs.py --check-repository .

check-large-files:
	$(PYTHON) scripts/check_repository_files.py --root . --max-mb 20
