# PROPOSALS — critic-architecture

- **Run:** 2026-10-29, `python3 codegraph.py --json reports/latest.json`
- **Evidence:** `reports/latest.txt`, `reports/latest.json`
- **Status:** proposals only — nothing outside this folder was modified.

## Measured

- 28 public declarations in `include/` (`hydra_*`, `hydra2_*`);
  **0 declared-but-unused** after the typedef filter.
- 50 names defined in more than one source file (name-level heuristic).
- Largest units by line count are listed in the report for context.

| ID | Finding | Evidence (both `file:line` / report row) | Structural rule | Proposed change | Risk if unchanged |
|---|---|---|---|---|---|
| CA-1 | `_decode_bf16` exists twice | `tools/gguf_reader.py:576` and `tools/safetensors_to_hydra.py:229` | R12 (one implementation), R9 (compare parallel implementations) | before merging them, run both on the same byte inputs and compare the outputs (R9); then keep one and call it from both tools | two bf16 decoders drift, and a conversion bug becomes tool-dependent |
| CA-2 | `_load_core` and `extra` appear in all six `.subagents/*/codegraph.py` | 6 files, by design | R12 | none: the owner requires every sub-agent to have its own runnable script; the shared logic lives in `.subagents/tools/codegraph_core.py` | n/a — accepted split, recorded so it is not re-filed |
| CA-3 | `hydra_kv_cache_t` was reported as a dead declaration by the first run | `include/hydra_model.h` | — | already fixed in the checker: `*_t` names are typedefs, not functions | a noisy critic gets ignored |

## Method

```bash
python3 .subagents/critic-architecture/codegraph.py --json reports/latest.json
grep -n "_decode_bf16" tools/gguf_reader.py tools/safetensors_to_hydra.py
```

## Open

- CA-1 needs the R9 comparison run before any merge decision; this sub-agent
  does not execute code changes.
- Peer review of the other five `PROPOSALS.md` files: no proposal creates a second
  source of truth; SV-3, TS-1 and CE-1 are additive documentation or wiring work.

## Status — closed 2026-10-29 (round 13)

CA-1 closed, comparison first: both `_decode_bf16` bodies were run over all 65536
BF16 patterns and compared against each other and a reference (0 mismatches;
0 against the reference for every non-NaN pattern, 254 NaN patterns excluded from
the payload comparison), then the conversion moved to `tools/bf16.py`. Both tools
keep a two-line adapter that only re-types the error, so the duplicate NAME
remains (this check still lists it) while the duplicate RULE is gone.
`tools/gguf_test.py`: 101 checks, 0 failed, including the safetensors round trip.
