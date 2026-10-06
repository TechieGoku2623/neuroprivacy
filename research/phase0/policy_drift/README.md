# policy_drift

## What is measured

How often five vendors change a dated privacy-policy snapshot across 12 committed months of synthetic Wayback-style HTML.

## Why it decides something

The change rate sets the monitoring cadence. Monthly polling is wasted if policies are static; quarterly polling misses mid-quarter clause removals if drift is high.

## How to run

```bash
uv run python research/phase0/policy_drift/run.py
```

Snapshots are synthetic and committed. This harness does not scrape live sites.
