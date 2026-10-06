# statute_coverage

## What is measured

What fraction of encoded Colorado HB24-1058 and California SB 1223 neural-data provisions are machine-checkable from policy text alone.

## Why it decides something

If most operative duties require network observation or internal records, Phase 2 should stay a policy-diff tool and keep capture optional. If a large share is policy-text-checkable, the extractor schema is the critical path.

## How to run

```bash
uv run python research/phase0/statute_coverage/run.py
```

Clause objects live in `src/neuroprivacy/statutes.py` and cite public statute text summaries.
