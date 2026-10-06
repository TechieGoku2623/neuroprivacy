# Phase 0 harnesses

`make research` runs these in order:

1. `extraction_accuracy/probe_set/build.py` — rebuild the 20 labeled policy snippets and the LLM cache
2. `extraction_accuracy/run.py` — per-field accuracy and Cohen's kappa
3. `statute_coverage/run.py` — CO/CA clause checkability from policy text
4. `policy_drift/probe_set/build.py` — rebuild 12 months × 5 vendors of synthetic snapshots
5. `policy_drift/run.py` — change rate and monitoring cadence
6. `render_docs.py` — write `docs/phase-0/research-memo.md`, `docs/EVALUATION.md`, `docs/DATA.md`, and the measured tables in `README.md`

No number in the memo is typed by hand. If a quantity cannot be produced here, the memo says **unmeasured** and names the measurement that would settle it.
