export PATH := $(HOME)/.local/bin:$(PATH)
UV ?= uv

.PHONY: setup lint test research eval demo record report

setup:
	$(UV) sync --extra dev

lint:
	$(UV) run ruff check src tests research
	$(UV) run ruff format --check src tests research
	$(UV) run mypy

test:
	$(UV) run pytest

research:
	$(UV) run python research/phase0/run_all.py

eval:
	$(UV) run python research/phase0/extraction_accuracy/run.py
	$(UV) run python research/phase0/statute_coverage/run.py
	$(UV) run python research/phase0/policy_drift/run.py
	$(UV) run python research/phase0/render_docs.py

demo:
	$(UV) run neuroprivacy demo

report:
	$(UV) run neuroprivacy report --out docs/report/index.html

record:
	$(UV) run python -c "from neuroprivacy.recordings import record_all; print(*record_all(), sep='\n')"
