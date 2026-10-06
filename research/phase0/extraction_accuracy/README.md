# extraction_accuracy

## What is measured

Per-schema-field precision, recall, and F1 of the Phase 0 span extractor against 20 hand-labeled synthetic policy documents. Cohen's kappa versus a keyword baseline, and Cohen's kappa of labeling pass 1 (committed gold) versus rater 2 (a simpler rules extractor with a different lexicon).

## Why it decides something

If per-field F1 is high and inter-rater kappa is stable, LLM extraction (or the current schema) is viable for Phase 2. If inter-rater kappa is low, the schema needs narrowing before any model is called. The keyword baseline is the control that must miss generic "device data" coverage.

## How to run

```bash
uv run python research/phase0/extraction_accuracy/run.py
```

Seed: none. The probe set is committed under `probe_set/documents.json` and rebuilt by `probe_set/build.py`.

## Gold-label source

Hand labels in `probe_set/build.py` (`values` on each document). They are not copied from `extract_rules`. Rater 2 is `extract_rater2`.
