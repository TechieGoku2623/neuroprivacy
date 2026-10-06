# Data

Phase 0 does not fetch live vendor policies or capture device traffic. The committed objects are:

- `data/sample/*.html` — four designed demo policies (vendor-a/b/c and two vendor-d snapshots; see `data/sample/README.md`)
- `data/sample/llm_cache.json` — prompt-hash-keyed extractor cache; no API key
- `research/phase0/extraction_accuracy/probe_set/documents.json` — 20 labeled synthetic snippets
- `research/phase0/policy_drift/probe_set/snapshots.json` — 60 synthetic monthly snapshots
- `src/neuroprivacy/statutes.py` — 22 encoded CO/CA clauses

No consumer-identifiable data. No authenticated scrape. License notes for the production sources (HB24-1058, SB 1223, public vendor pages) are in `docs/phase-0/research-memo.md` §3.
