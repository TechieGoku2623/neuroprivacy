export PATH := $(HOME)/.local/bin:$(PATH)
UV ?= uv

.PHONY: demo-shots setup lint test research eval demo record report

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

demo-shots:
	$(UV) run --with pyyaml python demo/verify_shots.py

record:
	bash demo/record.sh
	bash demo/render.sh
