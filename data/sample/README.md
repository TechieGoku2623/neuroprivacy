# Sample policy documents

These records are designed synthetic public-style HTML snippets, not scraped
pages and not documents behind authentication. Each one exists to exercise a
path the walkthrough names. `make demo` and `make test` run with no network.

Findings produced from these files are **observations**, not legal conclusions.

| File | Why it is here |
| --- | --- |
| `vendor-a.html` | Names neural data explicitly and grants a deletion right. Designed COMPLIANT observation. |
| `vendor-b.html` | Never uses neural/brain/EEG. Coverage is only under generic "device data". The keyword baseline misses this; the rules extractor should not. |
| `vendor-c.html` | Deletion clause contradicted by a retention clause. Status must be INDETERMINATE. |
| `vendor-d-2025-01.html` | January snapshot: neural data + third-party sharing clause. |
| `vendor-d-2025-06.html` | June snapshot: sharing clause removed. Drift/diff teaching case. |

`llm_cache.json` is a committed response cache keyed by SHA-256 prompt hash
for these documents. Phase 0 never calls a live LLM. Cache misses fall back
to the deterministic span extractor.

Public policies only. No circumvention. Network observation of devices is
gated and off.
